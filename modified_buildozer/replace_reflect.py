import os


package_name = (
    [
        line
        for line in open(f"{os.getcwd()}/buildozer.spec", "r").readlines()
        if line.startswith("package.name")
    ][0]
    .split("=")[1]
    .strip()
)

files_to_replace = [
    f"{os.getcwd()}/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/python-installs/{package_name}/arm64-v8a/jnius/reflect.py"
]

fixed_files = [
    file for file in os.listdir(f'{os.getcwd()}/modified_buildozer') if file == 'reflect.py'
]

for file in fixed_files:
    os.system(f"cp {os.getcwd()}/modified_buildozer/{file} {files_to_replace[0]}")