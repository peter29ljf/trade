   交易计划
  1 启动交易后，立即进行level0交易，先按照level 0 的tokenid ，查询一下目前这个id的价格，然后按照这个公式计算购买股份使用的usdc的amount0=profit/(1/price-1) ，然后发送level 0 的tokenid 和 amount0 进行交易。
  2 当我接收到btcprice 到125000 的时候，按照level 1 的tokenid ，查询一下目前这个id的价格，按照这个公式计算购买股份使用的usdc的amount1=(profit+amount0)/(1/price-1),然后发送level 1 的tokenid 和 amount1 进行交易。
  3 当我接收到btcprice 到130000 的时候，按照level 2 的tokenid ，查询一下目前这个id的价格，按照这个公式计算购买股份使用的usdc的amount2=(profit+amount1)/(1/price-1),然后发送level 2 的tokenid 和 amount2 进行交易。
 
  