import base

class CandInfoRatingClass(base.BaseRatingClass):
    data_key = "info"

    def _compute_data(self, cand):
        info = {}
        info["topo_period"] = cand.topo_period
        info["bary_period"] = cand.bary_period
        info["dm"] = cand.dm
        info["raj_deg"] = cand.raj_deg
        info["decj_deg"] = cand.decj_deg
        info["pfdfn"] = cand.pfdfn
        return info
