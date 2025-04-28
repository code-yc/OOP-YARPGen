import subprocess
import tempfile
import traceback
import time
import datetime
import os
import zipfile
import yaml
import random


def run_cmd(command: list, working_dir: str, timeout: int = 5):
    try:
        stdout_tmp = tempfile.SpooledTemporaryFile(buffering=16384)
        stderr_tmp = tempfile.SpooledTemporaryFile(buffering=1024)
        stdout_fileno = stdout_tmp.fileno()
        stderr_fileno = stderr_tmp.fileno()
        p = subprocess.Popen(command, cwd=working_dir, stdout=stdout_fileno, stderr=stderr_fileno, shell=False, close_fds=True)

        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if p.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                p.terminate()
                raise subprocess.TimeoutExpired(' '.join(command), timeout)
            time.sleep(0.1)
        # return p.stdout.read()

        stdout_tmp.seek(0)
        stdout = stdout_tmp.readlines()
        stdout = [x.decode('utf-8').strip() for x in stdout]

        stderr_tmp.seek(0)
        stderr = stderr_tmp.readlines()
        stderr = [x.decode('utf-8').strip() for x in stderr]
        return p.returncode, stdout, stderr

    except IOError:
        print(traceback.format_exc())
        return -1, [], []
    finally:
        if stdout_tmp:
            stdout_tmp.close()
        if stderr_tmp:
            stderr_tmp.close()


def get_current_time_str():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, '%Y-%m-%d-%H-%M')


def write_file(line: str, path: str, mode: str = 'a'):
    with open(path, mode) as file:
        file.write(line)


def dict_compare(d1: dict, d2: dict):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    shared_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
    same = set(o for o in shared_keys if d1[o] == d2[o])
    return added, removed, modified, same



def case_name_to_elf_name(compiler: str, case_file: str, opt: str, march = ""):
    return 'ELF-' + compiler.upper() + '-' + case_file + '-' + opt + march


def insert_to_dict(key: str, mapping: dict, new_value):
    if key not in mapping:
        mapping[key] = []
    mapping[key].append(new_value)

def filename_sort_key(filename):
    serial_number = filename.split('--')[-1].split('.')[0]
    return int(serial_number)

def delete_files_with_substring(directory, substring):
    for filename in os.listdir(directory):
        if substring in filename and os.path.isfile(os.path.join(directory, filename)):
            os.remove(os.path.join(directory, filename))


class LiteralString(str):
    pass

def literal_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

# 注册自定义的LiteralString
yaml.add_representer(LiteralString, literal_representer)

def generate_random_function_batch_from_zip(zip_path, batch_size, total_files):
    output_dir= "./"
    output_yaml_name= "functions.yaml"
    # 随机抽取不同编号
    random_ids = random.sample(range(1, total_files + 1), min(batch_size, total_files))

    merged_data = []

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for idx in random_ids:
            filename = f"func_{idx}.yaml"
            try:
                with zipf.open(filename) as file:
                    yaml_data = yaml.safe_load(file)
                    # 把 function 字段处理成 LiteralString，以便输出成 |- 样式
                    if 'function' in yaml_data:
                        yaml_data['function'] = LiteralString(yaml_data['function'].strip())
                    merged_data.append(yaml_data)
            except KeyError:
                print(f"Warning: {filename} not found in zip archive.")

    # 写出到一个新的yaml文件
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_yaml_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(merged_data, f, sort_keys=False, allow_unicode=True)