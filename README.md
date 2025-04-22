## Welcome to GitHub Pages

You can use the [editor on GitHub](https://github.com/Cchatnight/Cchatnight.github.io/edit/main/README.md) to maintain and preview the content for your website in Markdown files.

Whenever you commit to this repository, GitHub Pages will run [Jekyll](https://jekyllrb.com/) to rebuild the pages in your site, from the content in your Markdown files.

### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/Cchatnight/Cchatnight.github.io/settings/pages). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://docs.github.com/categories/github-pages-basics/) or [contact support](https://support.github.com/contact) and we’ll help you sort it out.


## Python test
### Pip
清华大学TUNA镜像源： https://pypi.tuna.tsinghua.edu.cn/simple  
https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple  
阿里云镜像源： http://mirrors.aliyun.com/pypi/simple/  
中国科学技术大学镜像源： https://mirrors.ustc.edu.cn/pypi/simple/    
华为云镜像源： https://repo.huaweicloud.com/repository/pypi/simple/  
腾讯云镜像源：https://mirrors.cloud.tencent.com/pypi/simple/  
hik源：http://af.hikvision.com.cn/artifactory/api/pypi/pypi/simple/  
官方：https://pypi.org/simple  

### 统计文件行数
1. readline读所有行
2. 依次读取每行
3. sum计数
    使用sum函数计数:n sum(1 for _ in open(file_name)
4. enumerate枚举计数:
```python
def enumerate_count(file_name):
    with open(file_name) as f:
        for count, _ in enumerate(f, 1):
            pass
    return count
```
5. buff count
每次读取固定大小,然后统计行数:
```python
def buff_count(file_name):
    with open(file_name, 'rb') as f:
        count = 0
        buf_size = 1024 * 1024
        buf = f.read(buf_size)
        while buf:
            count += buf.count(b'\n')
            buf = f.read(buf_size)
        return count
```
6. wc count
调用使用wc命令计算行
```python
def wc_count(file_name):
    import subprocess
    out = subprocess.getoutput("wc -l %s" % file_name)
    return int(out.split()[0])
```
7. partial count
在buff_count基础上引入partial:
```python
def partial_count(file_name):
    from functools import partial
    buffer = 1024 * 1024
    with open(file_name) as f:
        return sum(x.count('\n') for x in iter(partial(f.read, buffer), ''))
```
8. iter count 最优
在buff_count基础上引入itertools模块 :
```python
def iter_count(file_name):
    from itertools import (takewhile, repeat)
    buffer = 1024 * 1024
    with open(file_name) as f:
        buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
        return sum(buf.count('\n') for buf in buf_gen)
```
方法 100M 500M 1G 10G
readline_count 0.25 1.82 3.27 45.04
simple_count 0.13 0.85 1.58 13.53
sum_count 0.15 0.77 1.59 14.07
enumerate_count 0.15 0.80 1.60 13.37
buff_count 0.13 0.62 1.18 10.21
wc_count 0.09 0.53 0.99 9.47
partial_count 0.12 0.55 1.11 8.92
iter_count 0.08 0.42 0.83 8.33
