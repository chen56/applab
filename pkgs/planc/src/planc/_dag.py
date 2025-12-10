"""依赖集合排序：不允许循环依赖"""

from typing import TypeVar

# def topological_sort_dfs(dependencies_tree: dict[str, list[str]]) -> list[str]:
#     """依赖集合排序：不允许循环依赖.

#     Args:
#         dependencies_tree (dict): 依赖关系树，键为依赖项，值为被依赖项列表

#     Returns:
#         list: 拓扑排序后的节点列表

#     Examples:
#         >>> dependencies_tree = {
#              'A': ['B', 'C'],
#              'B': ['D'],
#              'C': ['E'],
#              'D': ['F'],
#              'E': ['G'],
#              'F': [],
#              'G': []
#          }
#         >>> topological_sort_dfs(dependencies_tree)
#         ['F', 'D', 'B', 'G', 'E', 'C', 'A']

#     Raises:
#         Exception: 当检测到循环依赖时抛出异常
#     """
#     adj_list = {}
#     all_nodes = set()

#     # 收集所有节点并初始化邻接表
#     for dependent, dependencies in dependencies_tree.items():
#         all_nodes.add(dependent)
#         if dependent not in adj_list:
#             adj_list[dependent] = set()
#         for dependency in dependencies:
#             all_nodes.add(dependency)
#             adj_list[dependent].add(dependency)
#             if dependency not in adj_list:
#                 adj_list[dependency] = set()

#     visited = set()
#     visiting = set()
#     result = []

#     def dfs(node):
#         visiting.add(node)
#         visited.add(node)

#         neighbors = adj_list.get(node, set())
#         for neighbor in neighbors:
#             if neighbor in visiting:
#                 # 使用 str(node) 来确保错误消息可读
#                 raise Exception(f"Cyclic dependency detected involving: {node} -> {neighbor}")
#             if neighbor not in visited:
#                 dfs(neighbor)

#         visiting.discard(node)
#         result.insert(0, node)  # 将节点加入结果的最前面

#     # 遍历所有节点，执行 DFS
#     for node in all_nodes:
#         if node not in visited:
#             dfs(node)

#     return result[::-1]


T = TypeVar("T")


def topological_sort_dfs(dependencies_tree: dict[T, list[T]]) -> list[T]:
    """拓扑排序的深度优先搜索实现，不允许循环依赖.

    Args:
        dependencies_tree (dict): 依赖关系树，键为依赖项，值为被依赖项列表

    Returns:
        list: 拓扑排序后的节点列表

    Examples:
        >>> dependencies = {
                "WebApp": ["API", "Database"],  # WebApp依赖API和Database
                "API": ["Utils"],                # API依赖Utils
                "Database": ["Utils"]            # Database依赖Utils
            }
        >>> topological_sort_dfs(dependencies)
        ['Utils', 'API', 'Database', 'WebApp']  # 正确的安装顺序

    Raises:
        Exception: 当检测到循环依赖时抛出异常
    """
    visited = {}
    result = []

    def dfs(node: T):
        if visited.get(node, 0) == 1:
            raise Exception(f"Detected circular dependency at: {node}")
        if visited.get(node, 0) == 2:
            return
        visited[node] = 1
        for dep in sorted(dependencies_tree.get(node, [])):
            dfs(dep)
        visited[node] = 2
        result.append(node)

    for node in sorted(dependencies_tree):
        dfs(node)

    return result
