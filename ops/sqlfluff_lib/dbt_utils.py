class DbtUtils:
    def generate_surrogate_key(self, *args, **kwargs):
        return "'dummy_surrogate_key'"

dbt_utils = DbtUtils()
