from odoo import http
from odoo.http import request


class ServiceApiController(http.Controller):

    VALID_TRANSITIONS = {
        "in_progress": "action_start",
        "done": "action_done",
    }

    def _error(self, code, message):
        return {"error": {"code": code, "message": message}}

    @http.route("/api/v1/interventions", type="jsonrpc",
                auth="user", methods=["POST"])
    def list_interventions(self, **kwargs):
        """Today's interventions visible to the logged-in user."""
        domain = [("state", "in", ["planned", "in_progress"])]
        records = request.env["service.intervention"].search_read(
            domain,
            ["name", "partner_id", "date_planned", "state"],
            limit=100)
        return {"count": len(records), "results": records}

    @http.route("/api/v1/interventions/<int:intervention_id>/status",
                type="jsonrpc", auth="user", methods=["POST"])
    def update_intervention_status(self, intervention_id, **kwargs):
        """Updates the status of an intervention for the logged-in technician."""

        if not isinstance(intervention_id, int) or intervention_id <= 0:
            return self._error(
                "invalid_id",
                "The intervention ID is invalid."
            )

        new_state = kwargs.get("state")
        if not new_state:
            return self._error(
                "missing_param",
                "The 'state' parameter is required."
            )

        if not isinstance(new_state, str):
            return self._error(
                "invalid_type",
                "The 'state' parameter must be a string."
            )

        if new_state not in self.VALID_TRANSITIONS:
            return self._error(
                "invalid_state",
                "Status '%s' is not supported. Allowed values: %s" % (
                    new_state,
                    ", ".join(self.VALID_TRANSITIONS.keys())
                )
            )

        intervention = request.env["service.intervention"].browse(
            intervention_id
        )
        if not intervention.exists():
            return self._error(
                "not_found",
                "Intervention not found or access denied."
            )

        method_name = self.VALID_TRANSITIONS[new_state]
        try:
            getattr(intervention, method_name)()
        except Exception as e:
            return self._error(
                "transition_failed",
                str(e)
            )

        return {
            "success": True,
            "id": intervention.id,
            "state": intervention.state,
        }