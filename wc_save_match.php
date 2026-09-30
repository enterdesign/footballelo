<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

define('ADMIN_PASSWORD', 'ucl2025');
define('MATCHES_FILE', __DIR__ . '/wc_matches.json');
define('TEAMS_EXTRA_FILE', __DIR__ . '/wc_teams_extra.json');
define('TEAM_MERGES_FILE', __DIR__ . '/wc_team_merges.json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) { http_response_code(400); echo json_encode(['error' => 'Invalid JSON']); exit; }

if (empty($input['password']) || $input['password'] !== ADMIN_PASSWORD) {
    http_response_code(401); echo json_encode(['error' => 'Invalid password']); exit;
}

// ── Helpers ─────────────────────────────────────────────────────────
function loadJsonFile($file, $default) {
    if (!file_exists($file)) return $default;
    $data = json_decode(file_get_contents($file), true);
    return is_null($data) ? $default : $data;
}
function saveJsonFile($file, $data) {
    file_put_contents($file, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
}
function teamExistsInMatches($matches, $name) {
    foreach ($matches as $m) {
        if (strcasecmp($m['teamA'] ?? '', $name) === 0 || strcasecmp($m['teamB'] ?? '', $name) === 0) return true;
    }
    return false;
}

if (!empty($input['action']) && $input['action'] === 'delete') {
    $idx = intval($input['index'] ?? -1);
    $matches = json_decode(file_get_contents(MATCHES_FILE), true);
    if ($idx < 0 || $idx >= count($matches)) { http_response_code(400); echo json_encode(['error' => 'Invalid index']); exit; }
    array_splice($matches, $idx, 1);
    file_put_contents(MATCHES_FILE, json_encode($matches, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    echo json_encode(['success' => true, 'total' => count($matches)]);
    exit;
}

// Handle: edit an existing match
if (!empty($input['action']) && $input['action'] === 'edit_match') {
    $idx = intval($input['index'] ?? -1);
    $matches = json_decode(file_get_contents(MATCHES_FILE), true);
    if ($idx < 0 || $idx >= count($matches)) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid index']);
        exit;
    }
    $phase = trim($input['phase'] ?? '');
    if ($phase === '') {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid phase']);
        exit;
    }
    $matches[$idx] = [
        'year'   => intval($input['year'] ?? 0),
        'phase'  => $phase,
        'teamA'  => trim($input['teamA'] ?? ''),
        'goalsA' => intval($input['goalsA'] ?? 0),
        'teamB'  => trim($input['teamB'] ?? ''),
        'goalsB' => intval($input['goalsB'] ?? 0),
    ];
    file_put_contents(MATCHES_FILE, json_encode($matches, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    echo json_encode(['success' => true, 'match' => $matches[$idx]]);
    exit;
}

// Handle: save phases config (K-values, labels, new phases)
if (!empty($input['action']) && $input['action'] === 'save_phases') {
    $phases = $input['phases'] ?? null;
    if (!is_array($phases) || empty($phases)) {
        http_response_code(400);
        echo json_encode(['error' => 'phases object is required']);
        exit;
    }
    $sanitized = [];
    foreach ($phases as $key => $ph) {
        $key = preg_replace('/\s+/', '', $key);
        if ($key === '') continue;
        $sanitized[$key] = [
            'label' => trim($ph['label'] ?? $key),
            'k'     => max(1, intval($ph['k'] ?? 8)),
            'color' => preg_match('/^#[0-9a-fA-F]{6}$/', $ph['color'] ?? '') ? $ph['color'] : '#60a5fa',
        ];
    }
    saveJsonFile(__DIR__ . '/wc_phases_config.json', $sanitized);
    echo json_encode(['success' => true, 'phases' => $sanitized]);
    exit;
}

// Handle: add a new national team placeholder (starts at base ELO, 0 matches)
if (!empty($input['action']) && $input['action'] === 'add_team') {
    $name = trim($input['name'] ?? '');
    if ($name === '') {
        http_response_code(400);
        echo json_encode(['error' => 'Team name is required']);
        exit;
    }
    $extra = loadJsonFile(TEAMS_EXTRA_FILE, []);
    if (!is_array($extra)) $extra = [];
    foreach ($extra as $t) {
        if (strcasecmp($t['name'] ?? '', $name) === 0) {
            http_response_code(400);
            echo json_encode(['error' => 'A team with that name already exists']);
            exit;
        }
    }
    $matches = loadJsonFile(MATCHES_FILE, []);
    if (teamExistsInMatches($matches, $name)) {
        http_response_code(400);
        echo json_encode(['error' => 'A team with that name already has match history']);
        exit;
    }
    $extra[] = [
        'name'   => $name,
        'region' => trim($input['region'] ?? 'UEFA'),
    ];
    saveJsonFile(TEAMS_EXTRA_FILE, $extra);
    echo json_encode(['success' => true, 'total' => count($extra)]);
    exit;
}

// Handle: remove a manually-added team placeholder (must have 0 matches)
if (!empty($input['action']) && $input['action'] === 'remove_team') {
    $name = trim($input['name'] ?? '');
    if ($name === '') {
        http_response_code(400);
        echo json_encode(['error' => 'Team name is required']);
        exit;
    }
    $matches = loadJsonFile(MATCHES_FILE, []);
    if (teamExistsInMatches($matches, $name)) {
        http_response_code(400);
        echo json_encode(['error' => 'Team has match history — merge it instead of removing']);
        exit;
    }
    $extra = loadJsonFile(TEAMS_EXTRA_FILE, []);
    if (!is_array($extra)) $extra = [];
    $found = false;
    $newExtra = [];
    foreach ($extra as $t) {
        if (strcasecmp($t['name'] ?? '', $name) === 0) { $found = true; continue; }
        $newExtra[] = $t;
    }
    if (!$found) {
        http_response_code(400);
        echo json_encode(['error' => 'Team not found in the manually-added list']);
        exit;
    }
    saveJsonFile(TEAMS_EXTRA_FILE, $newExtra);
    echo json_encode(['success' => true, 'total' => count($newExtra)]);
    exit;
}

// Handle: merge two teams into one (combines ELO history chronologically)
if (!empty($input['action']) && $input['action'] === 'merge_teams') {
    $teamA   = trim($input['teamA'] ?? '');
    $teamB   = trim($input['teamB'] ?? '');
    $newName = trim($input['newName'] ?? '');
    if ($teamA === '' || $teamB === '' || $newName === '') {
        http_response_code(400);
        echo json_encode(['error' => 'teamA, teamB and newName are required']);
        exit;
    }
    if (strcasecmp($teamA, $teamB) === 0) {
        http_response_code(400);
        echo json_encode(['error' => 'Choose two different teams']);
        exit;
    }

    $merges = loadJsonFile(TEAM_MERGES_FILE, []);
    if (!is_array($merges)) $merges = [];

    // Build tentative mapping (old name(s) -> new name)
    $tentative = $merges;
    if (strcasecmp($teamA, $newName) !== 0) $tentative[$teamA] = $newName;
    if (strcasecmp($teamB, $newName) !== 0) $tentative[$teamB] = $newName;

    // Cycle check: following the chain from newName must never loop back to teamA/teamB
    $cur = $newName;
    $hops = 0;
    while (isset($tentative[$cur]) && $hops < 50) {
        $cur = $tentative[$cur];
        if (strcasecmp($cur, $teamA) === 0 || strcasecmp($cur, $teamB) === 0) {
            http_response_code(400);
            echo json_encode(['error' => 'This merge would create a circular reference']);
            exit;
        }
        $hops++;
    }

    saveJsonFile(TEAM_MERGES_FILE, $tentative);

    // Update wc_teams_extra.json: drop placeholder entries for the old names,
    // upsert region info for the merged team's new name.
    $extra = loadJsonFile(TEAMS_EXTRA_FILE, []);
    if (!is_array($extra)) $extra = [];
    $newExtra = [];
    foreach ($extra as $t) {
        $n = $t['name'] ?? '';
        if (strcasecmp($n, $teamA) === 0 || strcasecmp($n, $teamB) === 0) continue;
        $newExtra[] = $t;
    }
    $region = trim($input['region'] ?? '');
    if ($region !== '') {
        $entry = ['name' => $newName, 'region' => $region];
        $upserted = false;
        foreach ($newExtra as &$t) {
            if (strcasecmp($t['name'] ?? '', $newName) === 0) { $t = $entry; $upserted = true; break; }
        }
        unset($t);
        if (!$upserted) $newExtra[] = $entry;
    }
    saveJsonFile(TEAMS_EXTRA_FILE, $newExtra);

    echo json_encode(['success' => true, 'merges' => $tentative]);
    exit;
}

$required = ['year', 'phase', 'teamA', 'goalsA', 'teamB', 'goalsB'];
foreach ($required as $field) {
    if (!isset($input[$field]) || $input[$field] === '') {
        http_response_code(400); echo json_encode(['error' => "Missing: $field"]); exit;
    }
}

// Accept any phase key — valid ones are defined in wc_phases_config.json
$phase = trim($input['phase']);
if ($phase === '') {
    http_response_code(400); echo json_encode(['error' => 'Invalid phase']); exit;
}
// Optionally validate against saved config if it exists
$phasesConfig = loadJsonFile(__DIR__ . '/wc_phases_config.json', []);
if (!empty($phasesConfig) && !array_key_exists($phase, $phasesConfig)) {
    // Also allow built-in defaults in case config not saved yet
    $builtIn = ['group', 'r16', 'qf', 'sf', '3rd', 'final'];
    if (!in_array($phase, $builtIn)) {
        http_response_code(400); echo json_encode(['error' => 'Invalid phase: "' . $phase . '" not in phases config']); exit;
    }
}

$match = [
    'year'   => intval($input['year']),
    'phase'  => $phase,
    'teamA'  => trim($input['teamA']),
    'goalsA' => intval($input['goalsA']),
    'teamB'  => trim($input['teamB']),
    'goalsB' => intval($input['goalsB']),
];

$matches = json_decode(file_get_contents(MATCHES_FILE), true) ?? [];
$matches[] = $match;
file_put_contents(MATCHES_FILE, json_encode($matches, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
echo json_encode(['success' => true, 'total' => count($matches), 'match' => $match]);
