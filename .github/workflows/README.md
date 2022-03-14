## Naming rule
```
[EVENT] CONTENT
```

## Workflows
> By default, [Push] includes a manual trigger (dispatch).

- `[Push] Build dev`
    - EVENT
        - When code is pushed to master
            - (triggered by `[Push] Sync CI`)
        - When the workflow is manually triggered
    - CONTENT
        - Build code and push docker image to pyengine
- `[Dispatch] Release`
    - EVENT
        - When the workflow is manually triggered
    - CONTENT
        - Build code and push docker image to pyengine and spaceone
- `[Push] Sync CI`
    - EVENT
        - When code is pushed to master
            - (trigger `[Push] Build dev`)
        - When the workflow is manually triggered    
    - CONTENT
        - [Push]
            - Get workflows from actions and Trigger `[Push] Build dev`
        - [Dispatch]
            - Just get workflows from actions
        
- `[PR] Review (TODO)`

## Scenario
- Release: 
    - Manually trigger `[Dispatch] Release`
- Build Dev (Push): 
    - Commit code to master branch(`[Push] Sync CI` -> `[Push] Build dev`)
- Build Dev (Dispatch): 
    - Manually trigger `[Push] Build dev`
- Update workflows: 
    - Manually trigger `[Push] Sync CI`
