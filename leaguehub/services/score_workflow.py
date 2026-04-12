from dataclasses import dataclass
from typing import Optional

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from leaguehub.models import Game, GameScoreAuditEntry, GameStatus, GameVerificationStatus
from leaguehub.services.permissions import can_edit_verified_game, can_submit_score, can_verify_score, is_league_admin


@dataclass
class ScoreWorkflowResult:
    game: Game
    audit_entry: Optional[GameScoreAuditEntry] = None


def _lock_game(game: Game) -> Game:
    return Game.objects.select_for_update().select_related("home_team", "away_team", "league_season").get(pk=game.pk)


def _validate_score_values(home_score: int, away_score: int):
    if home_score is None or away_score is None:
        raise ValidationError("Both home and away scores are required.")
    if home_score < 0 or away_score < 0:
        raise ValidationError("Scores cannot be negative.")


def _create_audit_entry(*, game: Game, edited_by, previous_state: dict, note: str = "", requires_reverification: bool = False):
    return GameScoreAuditEntry.objects.create(
        game=game,
        edited_by=edited_by,
        previous_home_score=previous_state["home_score"],
        previous_away_score=previous_state["away_score"],
        new_home_score=game.home_score,
        new_away_score=game.away_score,
        previous_status=previous_state["status"],
        new_status=game.status,
        previous_verification_status=previous_state["verification_status"],
        new_verification_status=game.verification_status,
        note=note,
        requires_reverification=requires_reverification,
    )


@transaction.atomic
def submit_home_score(*, game: Game, actor, home_score: int, away_score: int) -> ScoreWorkflowResult:
    locked_game = _lock_game(game)
    if not can_submit_score(actor, locked_game):
        raise PermissionDenied("Only the home head coach or an admin can submit the score.")
    if locked_game.verification_status == GameVerificationStatus.VERIFIED_FINAL and not can_edit_verified_game(actor, locked_game):
        raise ValidationError("Verified final games cannot be edited by non-admin users.")

    _validate_score_values(home_score, away_score)

    # Idempotent behavior: same submitted values on the same awaiting state return the locked game unchanged.
    if (
        locked_game.home_score == home_score
        and locked_game.away_score == away_score
        and locked_game.verification_status == GameVerificationStatus.AWAITING_AWAY_VERIFICATION
    ):
        return ScoreWorkflowResult(game=locked_game)

    previous_state = {
        "home_score": locked_game.home_score,
        "away_score": locked_game.away_score,
        "status": locked_game.status,
        "verification_status": locked_game.verification_status,
    }
    locked_game.home_score = home_score
    locked_game.away_score = away_score
    locked_game.status = GameStatus.FINAL
    locked_game.verification_status = GameVerificationStatus.AWAITING_AWAY_VERIFICATION
    locked_game.submitted_by = actor
    locked_game.submitted_at = timezone.now()
    locked_game.verified_by = None
    locked_game.verified_at = None
    locked_game.save()

    audit_entry = None
    if is_league_admin(actor) and previous_state["verification_status"] == GameVerificationStatus.VERIFIED_FINAL:
        audit_entry = _create_audit_entry(
            game=locked_game,
            edited_by=actor,
            previous_state=previous_state,
            note="Admin edited a previously verified final score.",
            requires_reverification=True,
        )
    return ScoreWorkflowResult(game=locked_game, audit_entry=audit_entry)


@transaction.atomic
def verify_game_score(*, game: Game, actor) -> ScoreWorkflowResult:
    locked_game = _lock_game(game)
    if not can_verify_score(actor, locked_game):
        raise PermissionDenied("Only the away head coach or an admin can verify the score.")
    if locked_game.verification_status == GameVerificationStatus.VERIFIED_FINAL:
        raise ValidationError("This game has already been verified.")
    if locked_game.verification_status != GameVerificationStatus.AWAITING_AWAY_VERIFICATION:
        raise ValidationError("A score must be submitted before it can be verified.")
    if not locked_game.has_valid_score:
        raise ValidationError("A valid score must exist before verification.")

    locked_game.status = GameStatus.FINAL
    locked_game.verification_status = GameVerificationStatus.VERIFIED_FINAL
    locked_game.verified_by = actor
    locked_game.verified_at = timezone.now()
    locked_game.save()
    return ScoreWorkflowResult(game=locked_game)


@transaction.atomic
def admin_override_score(
    *,
    game: Game,
    actor,
    home_score: int,
    away_score: int,
    note: str = "",
    require_reverification: bool = True,
) -> ScoreWorkflowResult:
    locked_game = _lock_game(game)
    if not is_league_admin(actor):
        raise PermissionDenied("Only admins can override scores.")

    _validate_score_values(home_score, away_score)
    previous_state = {
        "home_score": locked_game.home_score,
        "away_score": locked_game.away_score,
        "status": locked_game.status,
        "verification_status": locked_game.verification_status,
    }

    # Idempotent behavior for repeated admin overrides with identical values and same state.
    target_verification_status = (
        GameVerificationStatus.AWAITING_AWAY_VERIFICATION if require_reverification else GameVerificationStatus.VERIFIED_FINAL
    )
    if (
        locked_game.home_score == home_score
        and locked_game.away_score == away_score
        and locked_game.verification_status == target_verification_status
        and locked_game.status == GameStatus.FINAL
    ):
        return ScoreWorkflowResult(game=locked_game)

    locked_game.home_score = home_score
    locked_game.away_score = away_score
    locked_game.status = GameStatus.FINAL
    locked_game.verification_status = target_verification_status
    locked_game.submitted_by = actor
    locked_game.submitted_at = timezone.now()
    if require_reverification:
        locked_game.verified_by = None
        locked_game.verified_at = None
    else:
        locked_game.verified_by = actor
        locked_game.verified_at = timezone.now()
    locked_game.save()

    audit_entry = _create_audit_entry(
        game=locked_game,
        edited_by=actor,
        previous_state=previous_state,
        note=note or "Admin override score edit.",
        requires_reverification=require_reverification,
    )
    return ScoreWorkflowResult(game=locked_game, audit_entry=audit_entry)
