import logging
from typing import Dict, List

_LOGGER = logging.getLogger(__name__)


class BatchJobProcessor:
    """
    Batch Job 처리를 담당하는 재사용 가능한 헬퍼 클래스
    
    이 클래스는 Batch Job 데이터의 복잡한 처리 로직을 담당하며,
    다른 모듈에서도 재사용할 수 있도록 설계되었습니다.
    """
    
    def __init__(self, batch_connector):
        """
        Args:
            batch_connector: Batch API 커넥터 인스턴스
        """
        self.batch_connector = batch_connector
    
    def process_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Jobs 데이터를 효율적으로 처리합니다.
        
        Args:
            jobs: 처리할 Job 목록
            
        Returns:
            List[Dict]: 처리된 Job 목록
        """
        processed_jobs = []
        
        for job in jobs:
            try:
                processed_job = self._process_single_job(job)
                processed_jobs.append(processed_job)
            except Exception as e:
                job_name = job.get("name", "unknown")
                _LOGGER.error(f"Failed to process job {job_name}: {e}", exc_info=True)
                # 기본 job 정보라도 포함
                processed_jobs.append(self._create_basic_job_data(job))
        
        return processed_jobs
    
    def _process_single_job(self, job: Dict) -> Dict:
        """
        개별 Job을 처리합니다.
        
        Args:
            job: 처리할 Job 데이터
            
        Returns:
            Dict: 처리된 Job 데이터
        """
        # TaskGroup 처리
        task_groups = self._process_task_groups(
            job.get("taskGroups", []), job.get("allocationPolicy", {})
        )
        
        # Job 기본 정보
        return {
            "name": job.get("name", ""),
            "uid": job.get("uid", ""),
            "displayName": job.get("displayName", ""),
            "state": job.get("status", {}).get("state", ""),
            "createTime": job.get("createTime", ""),
            "updateTime": job.get("updateTime", ""),
            "taskGroups": task_groups,
        }
    
    def _process_task_groups(self, task_groups_raw: List[Dict], allocation_policy: Dict) -> List[Dict]:
        """
        TaskGroup들을 효율적으로 처리합니다.
        
        Args:
            task_groups_raw: 원본 TaskGroup 목록
            allocation_policy: 할당 정책
            
        Returns:
            List[Dict]: 처리된 TaskGroup 목록
        """
        instances = allocation_policy.get("instances", [])
        machine_type = ""
        if instances and instances[0].get("policy"):
            machine_type = instances[0]["policy"].get("machineType", "")
        
        processed_groups = []
        for task_group in task_groups_raw:
            try:
                processed_group = self._process_single_task_group(task_group, machine_type)
                processed_groups.append(processed_group)
            except Exception as e:
                group_name = task_group.get("name", "unknown")
                _LOGGER.error(f"Failed to process task group {group_name}: {e}", exc_info=True)
                # 기본 데이터라도 포함
                processed_groups.append(self._create_basic_task_group_data(task_group))
        
        return processed_groups
    
    def _process_single_task_group(self, task_group: Dict, machine_type: str) -> Dict:
        """
        개별 TaskGroup을 처리합니다.
        
        Args:
            task_group: TaskGroup 데이터
            machine_type: 머신 타입
            
        Returns:
            Dict: 처리된 TaskGroup 데이터
        """
        # 기본 정보 추출
        task_spec = task_group.get("taskSpec", {})
        runnables = task_spec.get("runnables", [])
        
        image_uri = ""
        if runnables and runnables[0].get("container"):
            image_uri = runnables[0]["container"].get("imageUri", "")
        
        compute_resource = task_spec.get("computeResource", {})
        
        # Tasks 수집 (최적화: 에러가 발생해도 계속 진행)
        tasks = self._collect_tasks_safe(task_group.get("name", ""))
        
        return {
            "name": task_group.get("name", ""),
            "taskCount": task_group.get("taskCount", "0"),
            "parallelism": task_group.get("parallelism", ""),
            "machineType": machine_type,
            "imageUri": image_uri,
            "cpuMilli": compute_resource.get("cpuMilli", ""),
            "memoryMib": compute_resource.get("memoryMib", ""),
            "tasks": tasks,
        }
    
    def _collect_tasks_safe(self, task_group_name: str) -> List[Dict]:
        """
        Tasks를 안전하게 수집합니다.
        
        Args:
            task_group_name: TaskGroup 이름
            
        Returns:
            List[Dict]: Task 목록
        """
        if not task_group_name:
            return []
        
        try:
            tasks = self.batch_connector.list_tasks(task_group_name)
            return [
                {
                    "name": task.get("name", ""),
                    "taskIndex": task.get("taskIndex", 0),
                    "state": task.get("status", {}).get("state", ""),
                    "createTime": task.get("createTime", ""),
                    "startTime": task.get("startTime", ""),
                    "endTime": task.get("endTime", ""),
                    "exitCode": task.get("status", {}).get("exitCode", 0),
                }
                for task in tasks
            ]
        except Exception as e:
            _LOGGER.error(f"Failed to collect tasks for {task_group_name}: {e}", exc_info=True)
            return []
    
    def _create_basic_job_data(self, job: Dict) -> Dict:
        """
        기본 Job 데이터를 생성합니다.
        
        Args:
            job: 원본 Job 데이터
            
        Returns:
            Dict: 기본 Job 데이터
        """
        return {
            "name": job.get("name", ""),
            "uid": job.get("uid", ""),
            "displayName": job.get("displayName", ""),
            "state": job.get("status", {}).get("state", "UNKNOWN"),
            "createTime": job.get("createTime", ""),
            "updateTime": job.get("updateTime", ""),
            "taskGroups": [],
        }
    
    def _create_basic_task_group_data(self, task_group: Dict) -> Dict:
        """
        기본 TaskGroup 데이터를 생성합니다.
        
        Args:
            task_group: 원본 TaskGroup 데이터
            
        Returns:
            Dict: 기본 TaskGroup 데이터
        """
        return {
            "name": task_group.get("name", ""),
            "taskCount": task_group.get("taskCount", "0"),
            "parallelism": task_group.get("parallelism", ""),
            "machineType": "",
            "imageUri": "",
            "cpuMilli": "",
            "memoryMib": "",
            "tasks": [],
        }
