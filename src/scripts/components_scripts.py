from graphframes import GraphFrame
import pyspark.sql.functions as F


def calculate_component(edges, ctype="weak"):
    
    edge_df = edges.select(["src", "dst"]).repartition(20).cache()
    node_df = edges.select(F.col("src").alias("id")).union(edges.select(F.col("dst").alias("id"))).groupby(["id"]).agg(F.lit(1).alias("_c"))
    
    g = GraphFrame(node_df, edge_df)
    if ctype == "weak":
        results = g.connectedComponents()
    elif ctype == "strong":
        results = g.stronglyConnectedComponents(maxIter=10)
    else:
        results = g.connectedComponents()

    results = results.select(["id", "component"]).withColumn("src", F.col("id"))
    size_count = results.groupby(["component"]).agg(F.count("id").alias("component_size")).filter("component_size>={size}".format(size=COMPONENT_SIZE_THRESHOLD))
    tmp_merge = results.join(size_count, ["component", ]).cache()

    edge_result = edges.join(tmp_merge, ["src"]).withColumnRenamed("src", "source").withColumnRenamed("dst", "target")
    node_result = node_df.join(tmp_merge, ["id"]).withColumnRenamed("id", "address").drop("src")

    return edge_result, node_result


def filtered_groups(groups):
    action_count = groups.groupby(["current_component", "address"]).agg(F.countDistinct("action").alias("_freq")).filter("_freq >={t}".format(t=GROUP_SIZE_THRESHOLD))
    action_filtered = groups.join(action_count, ["current_component", "address",]).drop("component_size").cache()

    address_count = action_filtered.groupby(["current_component", "component_id"]).agg(F.countDistinct("address").alias("component_size")).filter("component_size >={t}".format(t=COMPONENT_SIZE_THRESHOLD))
    result = action_filtered.join(address_count, ["current_component", "component_id",]).drop("_freq").cache()
    
    return result

    
def check_sybils(components):

    old_size = components.count()
    address_to_component = filtered_groups(components)
    current_size = address_to_component.count()
    while old_size > current_size and current_size > 0:
        old_size = current_size
        address_to_component = filtered_groups(address_to_component)
        current_size = address_to_component.count()

    return address_to_component

