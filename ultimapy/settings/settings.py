import os

try:
    from django.conf import settings  # noqa
except ModuleNotFoundError:
    settings = None

# if an environment file exists, load it into the env.
# if django exists, load the variables from the django config over the environment variable.
if os.path.exists('environment.ini'):
    env_file = open('environment.ini')
    for line in env_file:
        trim_line = line.rstrip('\n').strip()
        if not trim_line or trim_line.startswith("#"):
            continue
        if "=" not in trim_line:
            print(f"Skipping invalid environment.ini variable: '{trim_line}'")
        variable, value = trim_line.split('=')
        os.environ[variable] = value


def get_django_var_or_env(variable_name):
    return getattr(
        settings,
        variable_name,
        os.environ.get(variable_name, None)
    )


def ultima_file_path(file_name):
    return os.path.join(ULTIMA_FILES_DIR, file_name)


ULTIMA_MOUNT_IDS = get_django_var_or_env('MOUNT_IDS')
if type(ULTIMA_MOUNT_IDS) is str:
    import json
    ULTIMA_MOUNT_IDS = json.loads(ULTIMA_MOUNT_IDS)

if not ULTIMA_MOUNT_IDS:
    ULTIMA_MOUNT_IDS = [
        228, 200, 218, 204, 179, 226, 219, 116, 178, 220, 210, 117
    ]

ULTIMA_FILES_DIR = os.path.abspath(get_django_var_or_env('ULTIMA_FILES_DIR'))
