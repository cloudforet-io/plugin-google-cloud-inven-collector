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
        job_name = job.get("name", "")
        task_groups_raw = job.get("taskGroups", [])
        
        # 디버깅: Job에 TaskGroup이 있는지 확인
        # TaskGroup 정보가 없으면 추가 소스에서 확인
        if len(task_groups_raw) == 0:
            # Job spec에서 TaskGroup 확인
            job_spec = job.get("spec", {})
            if job_spec:
                task_groups_raw = job_spec.get("taskGroups", [])
            
            # 여전히 없으면 상세 정보 가져오기 시도
            if len(task_groups_raw) == 0:
                try:
                    detailed_job = self.batch_connector.get_job_details(job_name)
                    if detailed_job:
                        # 상세 정보에서 spec 확인 후 직접 taskGroups 확인
                        detailed_spec = detailed_job.get("spec", {})
                        if detailed_spec:
                            task_groups_raw = detailed_spec.get("taskGroups", [])
                        
                        if len(task_groups_raw) == 0:
                            task_groups_raw = detailed_job.get("taskGroups", [])
                except Exception as e:
                    _LOGGER.warning(f"Failed to get detailed job info for {job_name}: {e}")
        
        _LOGGER.debug(f"Processing job {job_name}: found {len(task_groups_raw)} task groups")
        
        # TaskGroup 처리 (Job 이름 전달)
        task_groups = self._process_task_groups(
            task_groups_raw, job.get("allocationPolicy", {}), job_name
        )
        
        # Job 기본 정보
        return {
            "name": job_name,
            "uid": job.get("uid", ""),
            "display_name": job.get("displayName", ""),
            "state": job.get("status", {}).get("state", ""),
            "create_time": job.get("createTime", ""),
            "update_time": job.get("updateTime", ""),
            "task_groups": task_groups,
        }
    
    def _process_task_groups(self, task_groups_raw: List[Dict], allocation_policy: Dict, job_name: str) -> List[Dict]:
        """
        TaskGroup들을 효율적으로 처리합니다.
        
        Args:
            task_groups_raw: 원본 TaskGroup 목록
            allocation_policy: 할당 정책
            job_name: Job의 전체 경로명
            
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
                processed_group = self._process_single_task_group(task_group, machine_type, job_name)
                processed_groups.append(processed_group)
            except Exception as e:
                group_name = task_group.get("name", "unknown")
                _LOGGER.error(f"Failed to process task group {group_name}: {e}", exc_info=True)
                # 기본 데이터라도 포함
                processed_groups.append(self._create_basic_task_group_data(task_group))
        
        return processed_groups
    
    def _process_single_task_group(self, task_group: Dict, machine_type: str, job_name: str) -> Dict:
        """
        개별 TaskGroup을 처리합니다.
        
        Args:
            task_group: TaskGroup 데이터
            machine_type: 머신 타입
            job_name: Job의 전체 경로명
            
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
        
        # TaskGroup 전체 경로 생성
        task_group_name = task_group.get("name", "")
        
        # TaskGroup name이 이미 전체 경로인지 확인
        if task_group_name and task_group_name.startswith("projects/"):
            # 이미 전체 경로
            full_task_group_path = task_group_name
        else:
            # 부분 경로이므로 job_name과 조합
            full_task_group_path = f"{job_name}/taskGroups/{task_group_name}" if task_group_name else ""
        
        # Tasks 수집 (최적화: 에러가 발생해도 계속 진행)
        tasks = self._collect_tasks_safe(full_task_group_path)
        
        return {
            "name": task_group_name,
            "task_count": task_group.get("taskCount", "0"),
            "parallelism": task_group.get("parallelism", ""),
            "machine_type": machine_type,
            "image_uri": image_uri,
            "cpu_milli": compute_resource.get("cpuMilli", ""),
            "memory_mib": compute_resource.get("memoryMib", ""),
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
            processed_tasks = []
            for task in tasks:
                status_events = task.get("status", {}).get("statusEvents", [])
                
                # 최신 이벤트 정보 추출 (eventTime 기준으로 최신)
                last_event_type = ""
                last_event_time = ""
                if status_events:
                    # eventTime 기준으로 정렬하여 최신 이벤트 찾기
                    sorted_events = sorted(
                        status_events,
                        key=lambda x: x.get("eventTime", ""),
                        reverse=True
                    )
                    latest_event = sorted_events[0]
                    last_event_type = latest_event.get("type", "")
                    last_event_time = latest_event.get("eventTime", "")
                
                processed_tasks.append({
                    "name": task.get("name", ""),
                    "state": task.get("status", {}).get("state", ""),
                    "status_events": status_events,
                    "last_event_type": last_event_type,
                    "last_event_time": last_event_time,
                })
            
            return processed_tasks
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
            "display_name": job.get("displayName", ""),
            "state": job.get("status", {}).get("state", "UNKNOWN"),
            "create_time": job.get("createTime", ""),
            "update_time": job.get("updateTime", ""),
            "task_groups": [],
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
            "task_count": task_group.get("taskCount", "0"),
            "parallelism": task_group.get("parallelism", ""),
            "machine_type": "",
            "image_uri": "",
            "cpu_milli": "",
            "memory_mib": "",
            "tasks": [],
        }
