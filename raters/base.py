import rating_classes

class BaseRater(object):
    name = NotImplemented
    description = NotImplemented
    version = NotImplemented

    def rate(self, cand):
        """Give a candidate rate it and return the rating value.

            Input:
                cand: A Candidate object to rate.

            Output:
                ratval: A RatingValue object.
        """
        value = self._compute_rating(cand)
        ratval = rating_value.RatingValue(self.name, self.version, \
                                            self.description, value)
        return ratval

    def _compute_rating(self, cand):
        """Give a candidate rate it and return the rating value.

            Input:
                cand: A Candidate object to rate.

            Output:
                value: A floating-point value - the rating value.
        """
        raise NotImplementedError("The '_compute_rating' method of " \
                                  "BaseRater should be overshadowed by " \
                                  "a full implementation by subclasses " \
                                  "of BaseRater.")
