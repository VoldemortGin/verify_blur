# verify_blur验收图片模糊工具说明

本工具只针对一图一标注的labelme格式. 其余格式需转换后再使用. 为统一处理, 只处理文件夹, 单一图片须将其与与对应的json标注文件放在一个文件夹内再处理.

## 0. 工作思路
先用mtl的crop工具, 把所有整图的实例扣出其最小外接矩形, 如有padding的话加上padding, 保存到一个临时文件夹`temp_crop`里. 

然后对`temp_crop`里的每张小图用拉普拉斯函数来计算边缘的二阶导数来判断图片是否模糊.

## 1. 整图划分保存到不同的文件夹
整图中, 只要有一个以上(包含一个)的缺陷标注框(实例分割时取其最小外接矩形, 如有padding的话加上padding)内为模糊的, 该张整图就保存到`blur_whole`文件夹内. 图名与原先相同.

如果一个模糊的缺陷框也没有, 那么该张整图保存到`distinct_whole`文件夹中.

标注json文件也复制一份到新的文件夹中.

## 2. 切图划分保存到不同的文件夹
每张图上的每个缺陷标注框(实例分割时取其最小外接矩形, 如有padding的话加上padding)为模糊的, 该框图就保存到`blur_crop`文件夹内. 切图的名字为`<原图名>_n.[jpg|png]`, n为这是这张图的第几个缺陷.

否则, 保存到`distinct_crop`文件夹中.



## 3. 配置

```yaml
task_name: 任务名可自取
blur_threshold: 过滤阈值(很重要一定要设)默认为2
canny_threshold_1: 100(建议默认)
canny_threshold_2: 200(建议默认)
padding: 10(建议默认)

base_dir: /Users/linhan/PycharmProjects/verify_blur(项目路径,一定要设)
labelme_dir: data/case_ls(原图路径,一定要设)
temp_dir: data/temp_crop(切图路径,一定要设)
#save_dir: data/temp_crop
blur_dir: data/blur(有模糊缺陷实例的整图放到这里)
distinct_dir: data/distinct(没有模糊缺陷实例的整图放到这里)
blur_crop_dir: data/blur_crop(模糊缺陷实例的切图放到这里)
distinct_crop_dir: data/distinct_crop(清晰缺陷实例的切图放到这里)
```

改完配置后直接运行.

## 4. 运行
```python
python main.py
```