from typing import Dict, Optional

from pydantic.v1 import BaseModel, root_validator

"""
@root_validator can be used very tricky-way to initialize the values.
"""


class S1(BaseModel):
    name: str = 'name'
    age: int = 65


class S2(S1):
    exp: Optional[str]
    desg: Optional[str]

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:

        values["name"] = "name"
        values["age"] = 10
        values["desg"] = "cxo"

        return values


class S3(S2):
    stage: Optional[str] = None


if __name__=='__main__':
    print("Test")
    s1 = S1(name="x", age=10)
    print(s1)
    s2 = S2(name="x", age=10, desg="cto")
    print(s2)

    s3 = S3()
    print(s3)
