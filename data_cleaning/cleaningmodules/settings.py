from .actions import OnOutlierDetect, OnDuplicateDetect, OnNullValue, OnFutureDate, OnForeignKeyViolation,\
    OnDenialConstraintViolation, OnFunctionalDependencyViolation
from .date_format_codes import format_codes


class Settings:
    def __init__(self):
        self.on_outlier_detect = OnOutlierDetect.FLAG
        self.on_duplicate_detect = OnDuplicateDetect.FLAG_ALL
        self.on_null_detect = OnNullValue.FLAG
        self.on_future_date_detect = OnFutureDate.FLAG
        self.date_format_code = 5
        self.on_foreign_key_violation = OnForeignKeyViolation.FLAG
        self.on_denial_constraint_violation = OnDenialConstraintViolation.FLAG
        self.on_functional_dependency_violation = OnFunctionalDependencyViolation.IGNORE
        self.enable_fds = False

    def set_outlier_action(self, action):
        """
        Set action (action = what must happen on outlier detection), type(action) == <class: OnOutlierDetect>
        :param action: integer representing the action (1,2,3 or 4)
        """
        if action in set([action.value for action in OnOutlierDetect]):
            self.on_outlier_detect = OnOutlierDetect(action)

    def set_duplicate_action(self, action):
        """
        Set action (action  what must happen on duplicate detection), type(action == <class: OnDuplicateDetect>
        :param action: integer representing the action (1,2,3 or 4)
        """
        if action in set([action.value for action in OnDuplicateDetect]):
            self.on_duplicate_detect = OnDuplicateDetect(action)

    def set_null_action(self, action):
        """
        Set action (action  what must happen on null value detection), type(action == <class: OnNullValue>
        :param action: integer representing the action (1,2 or 3)
        """
        if action in set([action.value for action in OnNullValue]):
            self.on_null_detect = OnNullValue(action)

    def set_on_future_date_action(self, action):
        """
        Set action (action what must happen on future date detection), type(action == <class: OnFutureDate>
        :param action: integer representing the action
        """
        if action in set([action.value for action in OnFutureDate]):
            self.on_future_date_detect = OnFutureDate(action)

    def set_date_format_code(self, format_code):
        if format_code in format_codes:
            self.date_format_code = format_code

    def set_on_foreign_key_violation_action(self, action):
        if action in set([action.value for action in OnForeignKeyViolation]):
            self.on_foreign_key_violation = OnForeignKeyViolation(action)

    def set_on_denial_constraint_violation_action(self, action):
        if action in set([action.value for action in OnDenialConstraintViolation]):
            self.on_denial_constraint_violation = OnDenialConstraintViolation(action)

    def set_on_functional_dependency_violation_action(self, action):
        if action in set([action.value for action in OnFunctionalDependencyViolation]):
            self.on_functional_dependency_violation = OnFunctionalDependencyViolation(action)
