import unittest
from planc._dag import topological_sort_dfs

class TestTopologicalSortDFS(unittest.TestCase):

    def test_should_correctly_sort_a_simple_linear_dependency_of_services(self):
        """测试正确排序简单的线性服务依赖."""
        # LoadBalancer -> VM -> Database
        # 销毁顺序: LoadBalancer -> VM -> Database (拓扑排序结果: Database, VM, LoadBalancer)
        dependencies = {
            'LoadBalancer': ['VM'],
            'VM': ['Database'],
        }
        sorted_result = topological_sort_dfs(dependencies)
        self.assertEqual(sorted_result, ['Database', 'VM', 'LoadBalancer'])

    def test_should_not_throw_for_a_valid_diamond_dependency_in_microservices(self):
        """测试有效的微服务菱形依赖不抛出异常."""
        #         +-----------+
        #         |  WebApp   |
        #         +-----------+
        #           /     \
        #          /       \
        #         V         V
        # +-------------+ +--------------------+
        # | API         | | Database           |
        # +-------------+ +--------------------+
        #          \         /
        #           \       /
        #            V     V
        #         +---------------+
        #         | Cache         |
        #         +---------------+
        dependencies = {
            'WebApp': ['API', 'Database'],
            'API': ['Cache'],
            'Database': ['Cache'],
        }
        sorted_result = topological_sort_dfs(dependencies)

        # 验证拓扑排序的有效性
        self.assertIn(sorted_result, [
            ["Cache", "API", "Database", "WebApp"],
            ["Cache", "Database", "API", "WebApp"]
        ])
        self.assertEqual(sorted_result,['Cache', 'API', 'Database', 'WebApp'])

    def test_should_return_an_empty_array_for_an_empty_dependency_map(self):
        """测试空依赖映射返回空数组"""
        dependencies = {}
        sorted_result = topological_sort_dfs(dependencies)
        self.assertEqual(sorted_result, [])

    def test_should_return_the_node_itself_for_a_single_resource_with_no_dependencies(self):
        """测试无依赖的单个资源返回其本身"""
        dependencies = {
            'VM': [],
        }
        sorted_result = topological_sort_dfs(dependencies)
        self.assertEqual(sorted_result, ['VM'])

    def test_should_correctly_sort_with_multiple_disconnected_service_components(self):
        """测试多个不相连的服务组件正确排序"""
        # Frontend -> Backend
        # Analytics -> DataLake
        dependencies = {
            'Frontend': [],  # 添加缺失的节点
            'Backend': ['Frontend'],
            'Analytics_Dashboard': [],  # 添加缺失的节点
            'DataLake_Storage': ['Analytics_Dashboard'],
        }
        sorted_result = topological_sort_dfs(dependencies)
        # 验证拓扑排序的有效性
# ['Frontend', 'Analytics_Dashboard', 'DataLake_Storage', 'Backend']
        self.assertEqual(sorted_result, ['Frontend', 'Backend', 'Analytics_Dashboard', 'DataLake_Storage'])
        self.assertIn(sorted_result, [
            ["Analytics_Dashboard", "DataLake_Storage", "Frontend", "Backend"],
            ["Frontend", "Backend", "Analytics_Dashboard", "DataLake_Storage"]
        ])

    def test_should_handle_resources_with_no_dependencies_properly(self):
        """测试正确处理无依赖的资源（它们应出现在前面）"""
        dependencies = {
            'Database_Instance': [],  # 添加缺失的节点
            'Application_Server': ['Database_Instance'],
            'CDN_Distribution': [],
        }
        sorted_result = topological_sort_dfs(dependencies)
        # 验证拓扑排序的有效性
        self.assertIn(sorted_result, [
            ["Database_Instance", "CDN_Distribution", "Application_Server"],
            ["CDN_Distribution", "Database_Instance", "Application_Server"]
        ])

    def test_should_throw_an_error_for_a_direct_cyclic_dependency_between_two_services(self):
        """测试两个服务之间的直接循环依赖抛出错误"""
        # ServiceA -> ServiceB -> ServiceA
        dependencies = {
            'ServiceA': ['ServiceB'],
            'ServiceB': ['ServiceA'],
        }
        with self.assertRaises(Exception) as context:
            topological_sort_dfs(dependencies)
        self.assertIn("Cyclic dependency detected involving", str(context.exception))

    def test_should_throw_an_error_for_a_longer_cyclic_dependency_chain(self):
        """测试较长的循环依赖链抛出错误"""
        # ComponentX -> ComponentY -> ComponentZ -> ComponentX
        dependencies = {
            'ComponentX': ['ComponentY'],
            'ComponentY': ['ComponentZ'],
            'ComponentZ': ['ComponentX'],
        }
        with self.assertRaises(Exception) as context:
            topological_sort_dfs(dependencies)
        self.assertIn("Cyclic dependency detected", str(context.exception))

    def test_should_throw_an_error_for_a_self_loop(self):
        """测试自循环（资源依赖自身）抛出错误"""
        # Self_Loop -> Self_Loop
        dependencies = {
            'Self_Loop': ['Self_Loop'],
        }
        with self.assertRaises(Exception) as context:
            topological_sort_dfs(dependencies)
        self.assertIn("Cyclic dependency detected", str(context.exception))


if __name__ == '__main__':
    unittest.main()
