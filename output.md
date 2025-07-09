# No title found




**在学习 Milvus 向量数据库时，除了本地 Milvus Lite、单机版 Milvus Standalone 或 Milvus on K8s 之外，还可以选择Zilliz Cloud—— 一种无需部署服务器、零成本上手的托管方案。下面将演示如何申请 Zilliz Cloud 中国区免费套餐并运行官方示例代码。**

我们本次实验使用的是国内站点，部署在阿里云，目前可以免费使用。

安装milvus-cli：

终端执行 milvus_cli，进入交互式 CLI

如果你使用的是 conda 也可以：

需要注意的是，在开源版本的 Milvus 中，端口号是9530 / 9091 ，而在Zilliz cloud 上，端口上是 443.

在config.ini中填入你的集群信息（务必保持格式），⚠️ 切勿把 API Key 提交到公开仓库。

运行后可见类似输出：

如果控制台显示如上日志，即表明已成功连接集群、创建 collection 并完成简单的向量检索。

然后我们就可以通过控制台来查看这个新建的索引和数据了。

除此之外，zilliz 还提供了restapi ，这样我们就可以通过请求 HTTP 来完成数据检索了。

Python 版本的如下，需要我们把api-key 作为 bear token 传到请求头里。

同样我们再 Postman 上也可以进行测试，需要注意的是，即使请求体是空的，那么也需要使用 {} 来占位。

在左侧的api-playground 中，我们可以看到更多的 API 操作，同时还可以直接在浏览器上发送请求。

通过 Zilliz Cloud，我们可以在几分钟内获得一套托管版 Milvus 服务，免去本地运维与资源成本，非常适合作为学习、原型开发或小型应用的向量数据库后端。祝大家玩得开心！






