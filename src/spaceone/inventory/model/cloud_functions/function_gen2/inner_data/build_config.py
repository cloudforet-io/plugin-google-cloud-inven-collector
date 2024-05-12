from schematics import Model
from schematics.types import ModelType, StringType, BooleanType, DictType

__all__ = ["BuildConfig"]


class StorageSource(Model):
    bucket = StringType(serialize_when_none=False)
    object = StringType(serialize_when_none=False)
    generation = StringType(serialize_when_none=False)


class RepoSource(Model):
    project_id = StringType(serialize_when_none=False, deserialize_from="projectId")
    repo_name = StringType(serialize_when_none=False, deserialize_from="repoName")
    dir = StringType(serialize_when_none=False)
    invert_regex = BooleanType(
        serialize_when_none=False, deserialize_from="invertRegex"
    )
    branch_name = StringType(serialize_when_none=False, deserialize_from="branchName")
    tag_name = StringType(serialize_when_none=False, deserialize_from="tagName")
    commit_sha = StringType(serialize_when_none=False, deserialize_from="commitSha")


class Source(Model):
    storage_source = ModelType(
        StorageSource, serialize_when_none=False, deserialize_from="storageSource"
    )
    repo_source = ModelType(
        RepoSource, serialize_when_none=False, deserialize_from="repoSource"
    )


class SourceProvenance(Model):
    resolved_storage_source = ModelType(
        StorageSource,
        serialize_when_none=False,
        deserialize_from="resolvedStorageSource",
    )
    resolved_repo_source = ModelType(
        RepoSource, serialize_when_none=False, deserialize_from="resolvedRepoSource"
    )


class BuildConfig(Model):
    build = StringType(serialize_when_none=False)
    runtime = StringType(serialize_when_none=False)
    entry_point = StringType(serialize_when_none=False, deserialize_from="entryPoint")
    source = ModelType(Source, serialize_when_none=False)
    source_provenance = ModelType(
        SourceProvenance, serialize_when_none=False, deserialize_from="sourceProvenance"
    )
    worker_pool = StringType(serialize_when_none=False, deserialize_from="workerPool")
    environment_variables = DictType(
        StringType, serialize_when_none=False, deserialize_from="environmentVariables"
    )
    docker_repository = StringType(
        serialize_when_none=False, deserialize_from="dockerRepository"
    )
