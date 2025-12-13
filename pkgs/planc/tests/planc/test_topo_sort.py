
import pytest
from planc._common import _topo_sort  # noqa: PyProtectedMember


class TestBasic:
    def test_should_correctly_sort_a_simple_linear_dependency_of_services(self):
        """测试正确排序简单的线性服务依赖."""
        # LoadBalancer -> VM -> Database
        # 销毁顺序: LoadBalancer -> VM -> Database (拓扑排序结果: Database, VM, LoadBalancer)
        dependencies = {
            "LoadBalancer": ["VM"],
            "VM": ["Database"],
        }

        sorted_result = _topo_sort(dependencies)
        assert sorted_result == ["Database", "VM", "LoadBalancer"]

    def test_should_not_throw_for_a_valid_diamond_dependency_in_microservices(self):
        """测试有效的微服务菱形依赖不抛出异常."""
        dependencies = {
            "WebApp": ["API", "Database"],
            "API": ["Cache"],
            "Database": ["Cache"],
        }
        sorted_result = _topo_sort(dependencies)
        assert sorted_result == ["Cache", "API", "Database", "WebApp"]

    def test_should_correctly_sort_with_multiple_disconnected_service_components(self):
        """测试多个不相连的服务组件正确排序"""
        dependencies = {
            "Backend": ["Frontend"],
            "Analytics": ["DataLake"],
        }
        sorted_result = _topo_sort(dependencies)
        assert sorted_result == ["DataLake", "Analytics", "Frontend", "Backend"]


class TestBoundaryConditions:
    def test_should_return_an_empty_array_for_an_empty_dependency_map(self):
        """测试空依赖映射返回空数组"""
        dependencies = {}
        sorted_result = _topo_sort(dependencies)
        assert sorted_result == []

    def test_should_return_the_node_itself_for_a_single_resource_with_no_dependencies(self):
        """测试无依赖的单个资源返回其本身"""
        dependencies = {
            "VM": [],
        }
        sorted_result = _topo_sort(dependencies)
        assert sorted_result == ["VM"]

    def test_should_handle_resources_with_no_dependencies_properly(self):
        """测试正确处理无依赖的资源"""
        dependencies = {
            "DB": [],
            "App": ["DB"],
            "CDN": [],
        }
        sorted_result = _topo_sort(dependencies)
        assert sorted_result == ["DB", "App", "CDN"]


class TestCircularDependency:  # 相当于 describe("UserFlows")
    def test_should_throw_an_error_for_a_direct_cyclic_dependency_between_two_services(self):
        """测试两个服务之间的直接循环依赖抛出错误"""
        dependencies = {
            "ServiceA": ["ServiceB"],
            "ServiceB": ["ServiceA"],
        }
        with pytest.raises(Exception, match="Detected circular dependency at: ServiceA"):
            _topo_sort(dependencies)

    def test_should_throw_an_error_for_a_longer_cyclic_dependency_chain(self):
        """测试较长的循环依赖链抛出错误"""
        dependencies = {
            "ComponentX": ["ComponentY"],
            "ComponentY": ["ComponentZ"],
            "ComponentZ": ["ComponentX"],
        }
        with pytest.raises(Exception, match="Detected circular dependency at: ComponentX"):
            _topo_sort(dependencies)

    def test_should_throw_an_error_for_a_self_loop(self):
        """测试自循环（资源依赖自身）抛出错误"""
        dependencies = {
            "Self_Loop": ["Self_Loop"],
        }
        with pytest.raises(Exception, match="Detected circular dependency at: Self_Loop"):
            _topo_sort(dependencies)
