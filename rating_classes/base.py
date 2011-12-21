class BaseRatingClass(object):
    data_key = "dummy"

    def add_data(self, cand):
        if not self.has_data(cand):
            for parent in self.__bases__:
                if issubclass(parent, BaseRatingClass):
                    parent.add_data(self, cand)
            data = self._compute_data(cand)
            cand.add_to_cache(data_key, data)

    def has_data(self, cand):
        return cand.is_in_cache(data_key)

    def get_data(self, cand):
        self.add_data(cand)
        return cand.get_from_cache(data_key)

    def _compute_data(self, cand):
        return None
        
