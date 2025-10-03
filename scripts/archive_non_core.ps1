# Moves non-core modules into archive/ with safety checks
Param(
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root '..')

function Move-Safe($source, $dest) {
  if (-not (Test-Path $source)) { return }
  if ($DryRun) { Write-Host "[DRYRUN] mv $source -> $dest"; return }
  New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
  Move-Item -Force $source $dest
}

$archive = Join-Path $repo 'archive'
New-Item -ItemType Directory -Force -Path $archive | Out-Null

# Roblox plugins
Move-Safe (Join-Path $repo 'VideoTo3D') (Join-Path $archive 'roblox_plugins\VideoTo3D')
Move-Safe (Join-Path $repo 'ModelForge-optimized\VideoTo3D') (Join-Path $archive 'roblox_plugins\ModelForge-optimized-VideoTo3D')
Move-Safe (Join-Path $repo 'prompt2roblox\plugin') (Join-Path $archive 'roblox_plugins\prompt2roblox-plugin')

# Lua inside ModelForge-1
Move-Safe (Join-Path $repo 'ModelForge-1\src') (Join-Path $archive 'roblox_plugins\ModelForge-1-src-lua')
Move-Safe (Join-Path $repo 'ModelForge-1\tests') (Join-Path $archive 'roblox_plugins\ModelForge-1-tests-lua')

# Optional experiments
foreach ($name in @('demo_enhanced_generation.py','nova_autogen_loop.py','nova_batch_generator.py','nova_enhanced_builder.py','nova_map_builder.py','youtube_to_model.py')) {
  $src = Join-Path $repo (Join-Path 'ModelForge-1' $name)
  if (Test-Path $src) { Move-Safe $src (Join-Path $archive (Join-Path 'experiments' $name)) }
}

# Create index README
$readme = Join-Path $archive 'ARCHIVED_README.md'
if (-not $DryRun) {
  @(
    '# Archived Modules',
    '',
    'This directory contains non-core modules preserved for historical and optional use.',
    '',
    'See root CLEANUP_PLAN.md for policy and rollback steps.'
  ) | Set-Content -Encoding UTF8 $readme
}

Write-Host 'Archive completed.'


