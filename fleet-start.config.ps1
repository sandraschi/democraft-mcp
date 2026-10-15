@{
    Name         = 'democraft-mcp'
    BackendPort  = 11246
    FrontendPort = 11245
    HealthPath   = '/api/health'
    WebRoot      = 'web_sota'

    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'democraft_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '11246' }
    }

    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
