import rdflib
from logger import log
from TravHarvConfigBuilder import AssertPath


class SubjPropPathAssertion:
    """
    A class to represent the assertion of all given property traversal paths for a given subject.
    """

    def __init__(self, subject: str, assertion_path: AssertPath):
        self.subject = subject
        self.assertion_path = assertion_path
        self.current_depth = 0
        self.previous_bounce_depth = 0
        self.assert_path()

    def assert_path(self):
        """
        Assert a property path for a given subject.
        """
        log.debug("Asserting a property path for a given subject")
        log.debug("Subject: {}".format(self.subject))
        # Implement method to assert a property path for a given subject
        while self.current_depth <= self.assertion_path.get_max_size():
            self._assert_at_depth()
            self._increase_depth()
        self._harvest_and_surface()

    def _assert_at_depth(self):
        """
        Assert a property path for a given subject at a given depth.
        """
        log.debug("Asserting a property path for a given subject at a given depth")
        log.debug("Depth: {}".format(self.current_depth))
        log.debug(
            "assertion_path: {}".format(
                self.assertion_path.get_path_for_depth(self.current_depth)
            )
        )
        # Implement method to assert a property path for a given subject at a given depth
        pass

    def _increase_depth(self):
        """
        Increase the depth of the property path assertion.
        """
        log.debug("Increasing the depth of the property path assertion")
        # Implement method to increase the depth of the property path assertion
        self.current_depth += 1

    def _harvest_and_surface(self):
        """
        Harvest the property path and surface back to depth 0.
        """
        log.debug("Harvesting the property path and backtracking to the previous depth")
        # Implement method to harvest the property path and backtrack to the previous depth
        self.previous_bounce_depth = self.current_depth
        self.current_depth = 0

    def _bail_out(self):
        """
        Bail out of the property path assertion.
        """
        log.debug("Bailing out of the property path assertion")
        return
