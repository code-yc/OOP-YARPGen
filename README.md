## OOP-YARPGen

基于随机程序生成器 YARPGen进行扩展，提供以下特性

- 结构体
- 面向对象
- 指针、动态内存分配
- 赋值关键词 (const, static等)
- 自定义函数注入



### 一、安装与部署

在项目根目录执行如下指令：

创建 `build` 文件夹

```
mkdir build
cd build
```

编译

```
cmake ..
make
```

执行成功后，产生名为 `yarpgen` 的文件，即可执行文件

```
./yarpgen
```

 生成的 `test.cpp` 即测试程序



### 二、测试脚本

测试脚本位于 `/runner` 路径下

#### 1、默认测试

通过执行如下命令，进行默认测试

```
python3 __main__.py
```

脚本会生成大量测试用例，并进行编译和运行。

在项目根目录的 `/Testing` 路径下，会产生一个名为测试时间的文件夹，其中：

- `/backup` 存放着可能存在bug的测试用例
- `/cases` 存放所有测试用例
- `/log` 存放所有测试日志信息



#### 2、自定义测试

通过 `/runner/default.yaml` 可以自定义测试规模

- language：一般无需改动
- generator_path：指 OOP-YARPGen 的可执行文件路径
- testing_path：测试文件夹路径，用于存放测试用例和日志
- timeout：编译的超时时间（以秒为单位）
- run_count：每次脚本生产的测试用例数量



#### 3、函数注入设置

- func_source_path：用户提供的函数 zip 包的路径
- func_batch_size： 每次生成包含的随机函数的个数
- func_total：函数 zip 包中函数的总数



#### 4、编译器设置

- compiler：用户指定的编译器列表
- optimization：用户指定的优化选项列表
- extra_option：用户指定的额外编译选项列表
- march：用户指定的架构列表



#### 三、函数注入功能

#### 1、指定函数

若需要在测试用例中注入自定义的函数，在 `/runner` 目录下 加入一个名为 `functions.yaml` 的文件：

```
# 示例函数 1
- function_name: func_1
  parameter_types:
  - int
  - float
  return_type: double
  function: |- 
    double func_1(int a, float b) {
      return a + b;
    }
  input:
  - '10'
  - '3.14'
  output: '13.14'
  misc:
  - const double PI = 3.14159;

# 示例函数 2
- function_name: func_2
  parameter_types:
  - void
  return_type: int
  function: |- 
    int func_2() {
      return VALUE;
    }
  input: []
  output: '20'
  misc:
  - const int VALUE = 20;
```

**必须是一个列表，且必须包含以下细节：**

1. **`function_name`**：名称
2. **`parameter_types`**：参数类型列表。若没有参数使用 `void`。
3. **`return_type`**：返回类型
4. **`function`**：完整代码，（ `|-` 表示的多行字符串）
5. **`input`**：输入参数值（字符串列表）
6. **`output`**：返回结果值（字符串）
7. **`misc`**：其他辅助信息，例如宏定义、常量等。



#### 2、函数库

若需要注入整个函数库，则通过 `/runner/default.yaml` 可以自定义函数库 zip 的路径和参数



**你需要提供一个 zip 压缩包，必须包含了 k 个 yaml 文件，名称必须为***

```
func_n.yaml		# n 从 0 到 k
```

**单个 yaml 格式必须如下：**

```
function_name: add
parameter_types:
- int
- int
return_type: int
function: |-  
  int add(int a, int b) {
      return a + b + VALUE;
  }
input:
- '1'
- '2'
output: '3'
misc:
- const int VALUE = 0;
```

