# Entity-Search
## 1.什么是Entity\_Search

Entity_Search能够帮助你从海量的实体-概念对(如包子-食物)文本中，查找你所提出的概念(如“金融”)所对应的实体。当然，如果文本的标记质量足够高，那么
工作将非常简单：只需要找出所有对应标记中存在“金融”的实体就可以了。但百科的编写者们常常没有一个统一的标准：他们可能会给“汇丰银行”标上“货币”、
“银行”...但就是忘了标上“金融”。这种情况并不少见，而Entity_Search所能做的，就是帮助你找出这些隐藏的实体。

## 2.Entity\_Search是如何工作的

回到之前的例子，尽管“汇丰银行”并没有被标上“金融”的标签，但它有“货币”、“银行”等标签，这些标签与金融具有非常紧密的关系(很多时候，也是从属关系)，以至于
我们可以认为有“货币”或“银行”标签的实体都应该被找到。因此，找到这些与核心概念“金融”关系密切的拓展标签就是任务的关键。

首先，我们自然需要找出所有标有核心概念“金融”的实体。这些实体的标签集合(我们称之为“拓展标签”)中，有许多可能与“金融” 有关，而更多则是无关紧要的。
区别这两者的重要依据，是在这些拓展标签对应的实体中，有多少实体的标记包括核心概念“金融”。举例来说，在实际
搜索过程中，我们常常会发现拓展标签中含有“中国”，但“中国”这一标签下的所有实体中，含有“金融”标签的无疑是凤毛麟角的。我们用pos\_proportion这一参数来记录这一关系(如“中国”标签下的实体中含有“金融”标签的个数/“中国”标签下的所有实体个数)。可以认为，pos\_proportion越低，这一标签与“金融”的重合度就越低。设置proportion阈值（程序中默认设置为0.32）之后，我们选择保留阈值之上的标签，往往可以取得很好的效果。

在这之后的工作就变得很简单了：找出拓展标签下的所有实体，它们与通过“金融”标签找到的实体一起组成了我们所需要的实体集合。这就是E\_S最常用的功能，而除此之外，E\_S还可以根据你给出的负概念（与“金融”完全无关的概念）进行实体的筛选，这将在函数的具体功能中介绍。

## 3.如何使用Entity\_Search
### 1.进行初始化
进行搜索前前，程序需要知道实体-概念对文件的存放位置(filename)，并读取文件，将其整理成字典以供调用。这一切只需要创建一个实例即可完成：

    import Entity_Search as ES
    searcher=ES.entity_find(filename)
### 2.给出核心概念并找出相应实体
完成实例的创建之后，就可以简单地进行搜索了。依然以“金融”为例，搜索需要运行这样一行代码：

    pos_entity,deleted=searcher.auto_search(core_tag='金融')

pos\_entity会被赋值为所有搜索到的实体构成的列表，deleted则是通过一些自动搜索出来的负概念被删除掉的实体。在默认参数delete=False下，不会进行删除实体的步骤，因此deleted一定为空列表。

您也可以输入列表作为参数，此时列表中的元素都将作为核心概念，统计pos\_proportion时，只需具有列表中的至少一个元素即可被记入，因此搜索到的实体只多不少。

    pos_entity,deleted=searcher.auto_search(core_tag=['金融','银行'])

如果有需要的话，你也可以通过调整函数的参数来调整搜索效果。函数的完整参数如下：

    pos_entity,deleted=search.auto_search(core_tag='金融',entity_dict=None,tag_dict=None,pos_threshold=0.32,\
    neg_threshold=0.1,freq_threshold=30,delete=False)

在这些参数中，只有core\_tag没有默认值，需要给出。pos\_threshold即为我们对pos\_proportion设置的阈值，对搜索效果的影响较为重要，降低pos\_threshold会提升找到的实体数量，但也可能会降低搜索结果的准确性。freq\_threshold和neg\_threshold在delete为False时没有作用。

*利用自动寻找的负概念进行筛选*

设置delete=True时，我们就可以利用自动筛选出的负概念对实体进行筛选。

    pos_entity,deleted=searcher.auto_search(core_tag='金融',delete=True)

在对实体进行筛选前，函数会先找出一些可能的负概念(即很可能与“金融”无关的概念)。这一步同样是根据pos\_proportion来做的-——但这一次，我们要取的候选集满足pos\_proportion<neg\_threshold。这些标签中有很多是非常大的概念（比如“专业”等），因此还需要满足标签下的实体数量小于freq\_threshold。在这之后，程序会将标签中含有负概念且没有核心概念“金融”的实体删除，存入deleted中以供查看。选择合适的neg\_proportion和freq\_threshold非常重要，若是不幸将较大的概念（如“专家”等）则可能会错误地删除正确的实体，因此需要根据情况选择合适的参数。

### 3.Entity\_Search的其他功能
#### 1.entity\_writer

在得到实体列表以后，使用entity\_writer可以方便地将实体列表保存为txt文件，存入指定路径s\_dir中

    ES.entity_writer(s_dir='金融实体.txt',entity_list=pos_entity)
    
#### 2.ES.entity\_find.search\_and\_writer
search\_and\_write的参数列表与auto\_search完全一致，返回值也一致。唯一的不同在于search\_and\_write会在运行中调用entity\_writer，将entity\_list保存成名称为核心概念+“实体.txt”的文件。如果输入概念列表作为参数，则文件名为列表的第一个元素。调用方法如下：

    pos_entity,deleted=searcher.auto_search(core_tag=['金融','银行'])
    
则生成的文件名为

<金融实体.txt

#### 3.ES.entity\_find.mannual\_search
一般而言，只有当负概念与核心概念完全无关时才能产生较好的筛选效果，这也导致自动筛选的负概念的效果很可能不尽如人意。如果您有一份手动筛选的负概念列表（形如neg\_tags=['武术','计算机','物理学']），则可以用mannual\_search来直接得到需要的实体：
    
    pos_entity,deleted=searcher.mannual_search(core_tag='金融',neg_tags=neg_tags,entity_dict=None,tag_dict=None,pos_threshold=0.32)
    
筛选过程与auto\_search是类似的，唯一的不同在于使用指定的负概念列表代替自动筛选出的负概念列表。

#### 4.ES.entity\_find.entity\_reduce
有时，您已经得到了一个实体列表(entity\_list)，但您也可能需要对它进行进一步的筛选工作。这时候，可以使用entity\_reduce：
    
    deleted=searcher.entity\_reduce(entity_list=entity_list,neg_tags=neg_tags,neg_entity=neg_entity)
    
除了使用负概念列表对实体进行筛选之外，还可以输入一个负实体列表neg\_entity，将它们从entity\_list中删除。返回值deleted为删除的所有实体，它们已经不存在于作为形参输入的entity\_list中。

    

    
