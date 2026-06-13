"""권한 유틸리티 및 검증 helper"""


def get_risky_permissions(permissions: dict) -> list[str]:
    """위험 권한 목록 반환"""
    risky = []
    if permissions.get("can_write_files"):
        risky.append("파일 쓰기")
    if permissions.get("can_execute_shell"):
        risky.append("쉘 실행")
    if permissions.get("can_use_internet"):
        risky.append("인터넷 접근")
    return risky


def validate_permissions(data: dict) -> dict:
    """권한 데이터 검증 - can_execute_shell은 admin에서만 true 가능"""
    # 현재는 단순 pass-through
    return data
