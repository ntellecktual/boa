path = r'boaapp\templates\boaapp\nfl_draft.html'
with open(path, 'a', encoding='utf-8') as f:
  f.write(r'''
<!-- ═══ ENGINEER PANE: Full Draft Room ═══ -->

<!-- PRE-DRAFT LOBBY -->
<div id="drLobby">
  <div class="dfr-lobby">
    <div class="dfr-lobby-hero">
      <div class="dfr-lobby-icon">&#x1F3C8;</div>
      <h1>2026 Fantasy Draft Room</h1>
      <p>12-team snake draft simulator with 9 AI archetypes, VOR-based rankings, and real-time analytics.</p>
      <div class="dfr-lobby-stats">
        <div class="dfr-lobby-stat"><div class="val">220+</div><div class="lbl">Players</div></div>
        <div class="dfr-lobby-stat"><div class="val">6</div><div class="lbl">Positions</div></div>
        <div class="dfr-lobby-stat"><div class="val">19</div><div class="lbl">Rounds</div></div>
        <div class="dfr-lobby-stat"><div class="val">9</div><div class="lbl">AI Strategies</div></div>
        <div class="dfr-lobby-stat"><div class="val">228</div><div class="lbl">Total Picks</div></div>
      </div>
    </div>
    <div class="dfr-settings">
      <div class="dfr-setting">
        <label>Scoring Format</label>
        <div class="dfr-fmt-btns" id="dfrFmtBtns">
          <button data-v="ppr" class="active">PPR</button>
          <button data-v="half">Half</button>
          <button data-v="std">Std</button>
        </div>
      </div>
      <div class="dfr-setting">
        <label>Your Pick Position</label>
        <select id="dfrPickPos">
          <option value="0">Pick 1 (First)</option>
          <option value="1">Pick 2</option>
          <option value="2">Pick 3</option>
          <option value="3">Pick 4</option>
          <option value="4">Pick 5</option>
          <option value="5">Pick 6</option>
          <option value="6">Pick 7</option>
          <option value="7">Pick 8</option>
          <option value="8">Pick 9</option>
          <option value="9">Pick 10</option>
          <option value="10">Pick 11</option>
          <option value="11" selected>Pick 12 (Last)</option>
        </select>
      </div>
      <div class="dfr-setting">
        <label>Pick Timer (seconds)</label>
        <select id="dfrTimerSel">
          <option value="0">No Timer</option>
          <option value="30" selected>30 sec</option>
          <option value="60">60 sec</option>
          <option value="90">90 sec</option>
          <option value="120">2 min</option>
        </select>
      </div>
    </div>
    <div>
      <p id="dfrLoadingMsg" style="display:none;font-size:.8rem;color:var(--dfr-muted);margin-bottom:.5rem">
        <i class="fas fa-spinner fa-spin me-1"></i> Loading projections&hellip;
      </p>
      <button class="dfr-enter-btn" id="dfrEnter">
        <i class="fas fa-door-open"></i> Enter Draft Room
      </button>
    </div>
    <div class="dfr-team-preview">
      <h3>Your Competition</h3>
      <div class="dfr-team-cards" id="dfrTeamCards"></div>
    </div>
  </div>
</div>

<!-- DRAFT ROOM -->
<div id="drRoom" style="display:none">
  <div class="dfr-room">
    <!-- Top Bar -->
    <div class="dfr-topbar">
      <div class="dfr-topbar-brand"><i class="fas fa-football-ball"></i> DRAFT ROOM</div>
      <div class="dfr-round-badge" id="dfrRoundBadge">RND 1 / 19</div>
      <div class="dfr-pick-badge" id="dfrPickBadge">Pick 0 / 228</div>
      <span id="dfrDataBadge" style="font-size:.58rem;font-weight:700;padding:.2rem .5rem;border-radius:6px;background:rgba(255,255,255,.08)">&#x1F4CB; OFFLINE</span>
      <div class="dfr-otc" id="dfrOTC">
        <div class="dfr-otc-label">ON THE CLOCK</div>
        <div class="dfr-otc-team">
          <div class="dfr-otc-dot" id="dfrOTCDot"></div>
          <span id="dfrOTCName">&#x2014;</span>
        </div>
      </div>
      <div class="dfr-timer" id="dfrTimer">
        <i class="fas fa-clock" style="font-size:.65rem;opacity:.6"></i>
        <div class="dfr-timer-val" id="dfrTimerVal">0:00</div>
      </div>
      <div class="dfr-topbar-controls">
        <button class="dfr-top-btn" id="dfrAutoBtn" title="Auto-pick for me">
          <i class="fas fa-robot"></i> AUTO
        </button>
        <button class="dfr-top-btn" id="dfrSimMyBtn" title="Sim to my pick">
          <i class="fas fa-forward"></i> SIM
        </button>
        <button class="dfr-top-btn" id="dfrSimAllBtn" title="Sim all remaining">
          <i class="fas fa-fast-forward"></i> ALL
        </button>
        <button class="dfr-top-btn" id="dfrPauseBtn" title="Pause / Resume">
          <i class="fas fa-pause"></i>
        </button>
        <button class="dfr-top-btn" id="dfrBoardBtn" title="View draft board">
          <i class="fas fa-th"></i>
        </button>
        <button class="dfr-top-btn" id="dfrExitBtn" title="Exit draft">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </div>
    <!-- Ticker -->
    <div class="dfr-ticker" id="dfrTicker"></div>
    <!-- 3-Column Main -->
    <div class="dfr-main">
      <!-- Left: Roster -->
      <div class="dfr-panel">
        <div class="dfr-panel-hd">
          <span><i class="fas fa-users"></i> YOUR ROSTER</span>
          <span class="count"><span id="dfrRosterCt">0/19</span> &middot; <span id="dfrRosterPts">0 pts</span></span>
        </div>
        <div class="dfr-roster" id="dfrRoster"></div>
        <div class="dfr-roster-footer">
          <span>Projected Pts</span>
          <span id="dfrRosterPtsFooter" style="color:var(--dfr-accent)">0</span>
        </div>
      </div>
      <!-- Center: Player Table -->
      <div class="dfr-players">
        <div class="dfr-toolbar">
          <input class="dfr-search" id="dfrSearch" type="text" placeholder="Search player or team&hellip;">
          <div class="dfr-pos-btns" id="dfrPosFilter">
            <button data-f="ALL" class="active">ALL</button>
            <button data-f="QB">QB</button>
            <button data-f="RB">RB</button>
            <button data-f="WR">WR</button>
            <button data-f="TE">TE</button>
            <button data-f="K">K</button>
            <button data-f="DST">DST</button>
          </div>
          <span class="dfr-sort-lbl">Sort: <span id="dfrSortLabel">VOR</span></span>
        </div>
        <div class="dfr-tbl-wrap">
          <table class="dfr-tbl">
            <thead>
              <tr>
                <th>#</th>
                <th>Player</th>
                <th data-col="pos">Pos</th>
                <th data-col="team">Team</th>
                <th data-col="bye">Bye</th>
                <th data-col="pts">Pts</th>
                <th data-col="vor">VOR</th>
                <th data-col="adp">ADP</th>
                <th>Pick</th>
              </tr>
            </thead>
            <tbody id="dfrPlayerBody"></tbody>
          </table>
        </div>
        <div class="dfr-ctrl-bar">
          <div class="dfr-speed-grp">
            <span>Speed:</span>
            <button class="dfr-speed-btn" data-sp="800">Slow</button>
            <button class="dfr-speed-btn active" data-sp="400">Med</button>
            <button class="dfr-speed-btn" data-sp="120">Fast</button>
            <button class="dfr-speed-btn" data-sp="20">Turbo</button>
          </div>
          <div class="dfr-progress">
            <div class="dfr-progress-bar"><div class="dfr-progress-fill" id="dfrProgressFill"></div></div>
            <div class="dfr-progress-text" id="dfrProgressText">0%</div>
          </div>
        </div>
      </div>
      <!-- Right: Feed -->
      <div class="dfr-panel" style="border-right:none;border-left:1px solid var(--dr-border)">
        <div class="dfr-panel-hd"><span><i class="fas fa-stream"></i> DRAFT FEED</span></div>
        <div class="dfr-feed" id="dfrFeed"></div>
      </div>
    </div>
  </div>
</div>

<!-- DRAFT BOARD OVERLAY -->
<div id="dfrBoardOverlay" class="dfr-board-overlay" style="display:none">
  <div class="dfr-board-modal">
    <div class="dfr-board-hd">
      <h4><i class="fas fa-th me-2"></i>Draft Board</h4>
      <button class="dfr-board-close" id="dfrBoardClose">&times;</button>
    </div>
    <div class="dfr-board-grid" id="dfrBoardGrid"></div>
  </div>
</div>

<!-- POST-DRAFT -->
<div id="drPost" style="display:none">
  <div class="dfr-post" id="dfrPostContent"></div>
</div>

  </div><!-- /engineer pane -->
</div><!-- /nd-demo -->
</section>

<!-- ═══ CLASSROOM ═══ -->
<section id="nd-classroom">
<div class="nd-cls">
  <div class="nd-section-label">Classroom</div>
  <h2 class="nd-section-title">Six Concepts That Drive Every Pick</h2>
  <p class="nd-section-sub">From the math behind VOR to the game theory of positional scarcity &mdash; understand the engine before you run it.</p>
  <div class="nd-cls-wrap">
    <div class="nd-cls-slides">

      <!-- Slide 1: VOR -->
      <div class="nd-cls-slide active">
        <span class="nd-cls-slide-icon">&#x1F4CA;</span>
        <div class="nd-cls-slide-num">Concept 01 of 06</div>
        <h3>Why VOR Beats Raw Points</h3>
        <p>A QB projecting 350 pts and a RB projecting 280 pts are not directly comparable. VOR (Value Over Replacement) subtracts the <em>replacement level</em> for each position &mdash; the best player freely available on waivers. The position with the steeper drop-off to replacement yields more VOR, and therefore more actual draft value.</p>
        <div class="nd-cls-code">vor = projected_pts - replacement_level_pts

# QB example (replacement = QB13, ~260 pts)
vor_qb = 350 - 260 = 90

# RB example (replacement = RB25, ~120 pts)
vor_rb = 280 - 120 = 160

# The RB ranks HIGHER despite fewer raw points.
# Scarcity wins.</div>
        <p style="font-size:.76rem;color:var(--nd-muted);margin:0"><strong>Key insight:</strong> RBs have far fewer viable starters than WRs, so the drop-off from elite to replacement RB is steeper. This is why elite RBs consistently go before elite QBs in real drafts.</p>
      </div>

      <!-- Slide 2: Snake Draft -->
      <div class="nd-cls-slide">
        <span class="nd-cls-slide-icon">&#x1F40D;</span>
        <div class="nd-cls-slide-num">Concept 02 of 06</div>
        <h3>Snake Draft: Position Is Everything</h3>
        <p>In a 12-team snake draft, pick order alternates each round. This creates an asymmetric information problem: you must predict which players will be available at your next pick slot, 23 picks away.</p>
        <table class="nd-cls-table">
          <thead><tr><th>Pick Slot</th><th>Round 1 Pick</th><th>Round 2 Pick</th><th>Gap</th><th>Advantage</th></tr></thead>
          <tbody>
            <tr><td>Pick 1</td><td>#1</td><td>#24</td><td>23 picks</td><td>Best player, long wait</td></tr>
            <tr><td>Pick 6</td><td>#6</td><td>#19</td><td>13 picks</td><td>Balanced exposure</td></tr>
            <tr><td>Pick 12</td><td>#12</td><td>#13</td><td>1 pick</td><td>Immediate double-dip</td></tr>
          </tbody>
        </table>
        <p style="font-size:.76rem;color:var(--nd-muted);margin:.5rem 0 0"><strong>Pick 12</strong> gets back-to-back picks in rounds 1&ndash;2, effectively securing two round-1-equivalent players. This is why the late-first-round slot is often considered the most strategically flexible position.</p>
      </div>

      <!-- Slide 3: AI Archetypes -->
      <div class="nd-cls-slide">
        <span class="nd-cls-slide-icon">&#x1F916;</span>
        <div class="nd-cls-slide-num">Concept 03 of 06</div>
        <h3>9 AI Archetypes, 9 Draft Stories</h3>
        <p>Each bot applies position-specific VOR multipliers. A RB with VOR 80 scores 124 composite points for Robust RB (80 &times; 1.55) but only 36 for Zero RB (80 &times; 0.45). Same player, wildly different perceived value.</p>
        <table class="nd-cls-table">
          <thead><tr><th>Strategy</th><th>QB</th><th>RB</th><th>WR</th><th>TE</th></tr></thead>
          <tbody>
            <tr><td><span class="nd-strat-pill">Robust RB</span></td><td>0.50&times;</td><td><strong>1.55&times;</strong></td><td>0.85&times;</td><td>0.60&times;</td></tr>
            <tr><td><span class="nd-strat-pill">Zero RB</span></td><td>0.70&times;</td><td>0.45&times;</td><td><strong>1.50&times;</strong></td><td>1.15&times;</td></tr>
            <tr><td><span class="nd-strat-pill">Hero RB</span></td><td>0.60&times;</td><td>1.10&times;</td><td>1.35&times;</td><td>0.75&times;</td></tr>
            <tr><td><span class="nd-strat-pill">TE Premium</span></td><td>0.65&times;</td><td>1.00&times;</td><td>1.00&times;</td><td><strong>1.70&times;</strong></td></tr>
            <tr><td><span class="nd-strat-pill">Late QB</span></td><td>0.25&times;</td><td>1.25&times;</td><td>1.25&times;</td><td>0.90&times;</td></tr>
            <tr><td><span class="nd-strat-pill">Balanced BPA</span></td><td>1.00&times;</td><td>1.00&times;</td><td>1.00&times;</td><td>1.00&times;</td></tr>
            <tr><td><span class="nd-strat-pill">Contrarian</span></td><td><strong>1.15&times;</strong></td><td>0.85&times;</td><td>0.85&times;</td><td>1.25&times;</td></tr>
          </tbody>
        </table>
      </div>

      <!-- Slide 4: Positional Scarcity -->
      <div class="nd-cls-slide">
        <span class="nd-cls-slide-icon">&#x1F4C9;</span>
        <div class="nd-cls-slide-num">Concept 04 of 06</div>
        <h3>Positional Scarcity: The Invisible Clock</h3>
        <p>Not all positions run dry at the same rate. In a 12-team, 2-RB, 2-WR league, there are 24 starting RB slots and 24 WR slots &mdash; but there are only 12&ndash;15 truly elite RBs while 28&ndash;32 viable WRs exist. The scarcity cliff hits RBs far harder.</p>
        <table class="nd-cls-table">
          <thead><tr><th>Position</th><th>Elite Starters</th><th>Replacement Drop-off</th><th>Draft Priority</th></tr></thead>
          <tbody>
            <tr><td>RB</td><td>12&ndash;15</td><td>High (RB25 = 48% of RB1)</td><td>&#x1F534; Urgent early</td></tr>
            <tr><td>WR</td><td>28&ndash;32</td><td>Medium (WR31 = 72% of WR1)</td><td>&#x1F7E1; Can wait</td></tr>
            <tr><td>TE</td><td>3&ndash;5 elite</td><td>Extreme (TE13 = 62% of TE1)</td><td>&#x1F7E0; Bi-modal</td></tr>
            <tr><td>QB</td><td>12 starters</td><td>Low (QB13 = 85% of QB1)</td><td>&#x1F7E2; Wait late</td></tr>
          </tbody>
        </table>
        <p style="font-size:.76rem;color:var(--nd-muted);margin:.5rem 0 0">TE is the most polarized: a Kelce or Bowers is worth a 2nd-round pick; the 13th TE is barely worth rostering. <strong>TE Premium</strong> bets on this gap; most others ignore it entirely.</p>
      </div>

      <!-- Slide 5: ADP vs VOR Arbitrage -->
      <div class="nd-cls-slide">
        <span class="nd-cls-slide-icon">&#x1F4A1;</span>
        <div class="nd-cls-slide-num">Concept 05 of 06</div>
        <h3>Finding Draft Value: ADP vs VOR</h3>
        <p>Average Draft Position (ADP) is the consensus market rank &mdash; where the crowd drafts a player on average. VOR rank is the algorithmic rank based purely on replacement-adjusted projected points. When these diverge, there is arbitrage.</p>
        <div class="nd-cls-code"># ADP vs VOR Arbitrage Detector
for player in sorted_by_vor:
    adp_rank  = player.adp
    vor_rank  = player.vor_rank
    discount  = adp_rank - vor_rank  # positive = undervalued

    if discount >= 15:
        print(f"{player.name}: drafted at pick {adp_rank}, "
              f"VOR says pick {vor_rank} (+{discount} free picks)")

# Example output:
# Trey Benson:   drafted pick 105, VOR rank 71  (+34)
# Jerome Ford:   drafted pick 91,  VOR rank 68  (+23)</div>
        <p style="font-size:.76rem;color:var(--nd-muted);margin:.5rem 0 0">The ADP &plusmn;8% jitter in the AI engine deliberately creates these gaps, simulating the cognitive biases and preference divergence that generate real draft value windows.</p>
      </div>

      <!-- Slide 6: Post-Draft Grading -->
      <div class="nd-cls-slide">
        <span class="nd-cls-slide-icon">&#x1F3C6;</span>
        <div class="nd-cls-slide-num">Concept 06 of 06</div>
        <h3>How the A&ndash;F Grade Is Calculated</h3>
        <p>Post-draft grading uses four metrics to rank all 12 teams and assign A+ through D letter grades based on finishing position in the league standings simulation.</p>
        <table class="nd-cls-table">
          <thead><tr><th>Metric</th><th>What It Measures</th><th>Penalty</th></tr></thead>
          <tbody>
            <tr><td><strong>Starter Pts</strong></td><td>Projected points from starting lineup (QB+2RB+2WR+TE+FLEX+K+DST)</td><td>Primary rank signal</td></tr>
            <tr><td><strong>Total VOR</strong></td><td>Sum of VOR for all 19 drafted players</td><td>Secondary tiebreaker</td></tr>
            <tr><td><strong>Bye Conflicts</strong></td><td>Weeks where 3+ starters share a bye week</td><td>&minus;1 grade tier each</td></tr>
            <tr><td><strong>Bench Depth</strong></td><td>Average bench player projected points</td><td>Informational</td></tr>
          </tbody>
        </table>
        <p style="font-size:.76rem;color:var(--nd-muted);margin:.5rem 0 0"><strong>Grades A+ &rarr; D</strong> are assigned by finishing rank (1st = A+, 2nd = A, 3rd = A, etc.) then adjusted down for each bye-week concentration penalty.</p>
      </div>

    </div><!-- /slides -->
    <div class="nd-cls-nav">
      <button class="nd-cls-btn" onclick="ndClsPrev()"><i class="fas fa-chevron-left me-1"></i> Prev</button>
      <div class="nd-cls-dots" id="ndClsDots">
        <button class="nd-cls-dot active" onclick="ndGotoClsDot(0)"></button>
        <button class="nd-cls-dot" onclick="ndGotoClsDot(1)"></button>
        <button class="nd-cls-dot" onclick="ndGotoClsDot(2)"></button>
        <button class="nd-cls-dot" onclick="ndGotoClsDot(3)"></button>
        <button class="nd-cls-dot" onclick="ndGotoClsDot(4)"></button>
        <button class="nd-cls-dot" onclick="ndGotoClsDot(5)"></button>
      </div>
      <button class="nd-cls-btn" onclick="ndClsNext()">Next <i class="fas fa-chevron-right ms-1"></i></button>
    </div>
  </div><!-- /cls-wrap -->
</div>
</section>

<!-- ═══ KEY POINTS ═══ -->
<section id="nd-keypoints">
<div class="nd-kps">
  <div class="nd-section-label">Key Points</div>
  <h2 class="nd-section-title">Four Engineering Decisions That Matter</h2>
  <p class="nd-section-sub">Why the simulator behaves the way it does &mdash; each choice reflects a real fantasy football principle with a measurable effect on draft outcomes.</p>
  <div class="nd-kps-grid">
    <div class="nd-kp">
      <span class="nd-kp-icon">&#x1F522;</span>
      <div class="nd-kp-label">Ranking Methodology</div>
      <h4>VOR Over Raw Points</h4>
      <p>A QB scoring 350 pts and a RB scoring 250 pts aren&apos;t comparable. VOR subtracts the replacement-level baseline per position (QB13, RB25, WR25, TE13 in a 12-team league). After VOR adjustment, the RB often ranks <strong>higher</strong> because the RB1&rarr;RB25 drop-off is twice as steep as QB1&rarr;QB13. This is why elite RBs routinely go before elite QBs in real drafts.</p>
    </div>
    <div class="nd-kp">
      <span class="nd-kp-icon">&#x1F916;</span>
      <div class="nd-kp-label">AI Design</div>
      <h4>9 Archetypes, Not One Optimal Bot</h4>
      <p>Real drafts have diverse strategies. Zero RB exploits waiver-wire RB value; Robust RB locks in scarce positional value early; TE Premium bets on the extreme scarcity cliff at tight end. By modeling 9 real strategies, the simulator creates realistic positional runs, reaches, and value falls that a single-strategy AI would never produce. Draft variance requires behavioral diversity.</p>
    </div>
    <div class="nd-kp">
      <span class="nd-kp-icon">&#x1F3AF;</span>
      <div class="nd-kp-label">Behavioral Realism</div>
      <h4>&plusmn;8% Jitter Creates Realistic Variance</h4>
      <p>Perfect AI play is boring and unrealistic. Real drafters have biases, sleeper picks, and team preferences. The <code style="font-size:.68rem;background:rgba(1,51,105,.06);padding:.1rem .3rem;border-radius:4px">val *= (0.92 + Math.random() * 0.16)</code> jitter causes occasional reaches (3&ndash;5 picks early) and steals (player falls unexpectedly), creating the variance that makes each draft unique and strategically meaningful.</p>
    </div>
    <div class="nd-kp">
      <span class="nd-kp-icon">&#x1F4E1;</span>
      <div class="nd-kp-label">Live Data Integration</div>
      <h4>SportsData.io Projections with Fallback</h4>
      <p>On load, the simulator fetches live 2026 season projections and ADP from <strong>SportsData.io</strong> via two API endpoints (player projections + DST). If the API fails or returns insufficient data (&lt;60 players), it silently falls back to hardcoded 2026 projections &mdash; a graceful degradation pattern that keeps the demo functional regardless of external API availability.</p>
    </div>
  </div>
</div>
</section>

<!-- ═══ CODE ═══ -->
<section id="nd-code">
<div class="nd-code">
  <div class="nd-section-label">Production Code</div>
  <h2 class="nd-section-title">Core Algorithms</h2>
  <p class="nd-section-sub">The Python implementations behind VOR ranking, AI strategy weighting, snake order generation, and post-draft grading.</p>

  <details>
    <summary>&#x1F9EE; VOR Calculation Engine (Python)</summary>
    <pre>
# ── Value Over Replacement (VOR) Calculation ──────────────────────
# VOR normalizes fantasy points across positions by subtracting
# the "replacement level" — the best player available on waivers.

def compute_vor(players: list[dict], league_size: int = 12) -> list[dict]:
    """
    Compute VOR for each player.
    Replacement level = the (N+1)th player at each position,
    where N = starting slots × league_size.
    """
    # Replacement thresholds: how many starters exist league-wide
    # QB1 × 12 = 12 starters → replacement = QB13
    # RB1-RB2 × 12 = 24 starters → replacement = RB25
    starters_per_team = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "K": 1, "DST": 1}
    replacement_rank = {
        pos: (slots * league_size) + 1
        for pos, slots in starters_per_team.items()
    }
    # e.g. {"QB": 13, "RB": 25, "WR": 25, "TE": 13, "K": 13, "DST": 13}

    from collections import defaultdict
    by_pos = defaultdict(list)
    for p in players:
        by_pos[p["pos"]].append(p)
    for pos in by_pos:
        by_pos[pos].sort(key=lambda x: x["projected_pts"], reverse=True)

    replacement_pts = {}
    for pos, rank in replacement_rank.items():
        idx = min(rank - 1, len(by_pos[pos]) - 1)
        replacement_pts[pos] = by_pos[pos][idx]["projected_pts"] if idx >= 0 else 0

    for p in players:
        p["vor"] = round(p["projected_pts"] - replacement_pts[p["pos"]], 1)

    players.sort(key=lambda x: x["vor"], reverse=True)
    return players

# Example: QB with 350 pts, replacement QB13 = 260 pts → VOR = 90
#          RB with 280 pts, replacement RB25 = 120 pts → VOR = 160
#          The RB ranks HIGHER despite fewer raw points — scarcity wins.</pre>
  </details>

  <details>
    <summary>&#x1F916; AI Draft Strategy Engine (Python)</summary>
    <pre>
# ── AI Draft Strategy: Weighted VOR with Archetype Biases ─────────

STRATEGIES = {
    "Robust RB":    {"QB": 0.50, "RB": 1.55, "WR": 0.85, "TE": 0.60, "K": 0.30, "DST": 0.30},
    "Zero RB":      {"QB": 0.70, "RB": 0.45, "WR": 1.50, "TE": 1.15, "K": 0.30, "DST": 0.30},
    "Hero RB":      {"QB": 0.60, "RB": 1.10, "WR": 1.35, "TE": 0.75, "K": 0.30, "DST": 0.30},
    "TE Premium":   {"QB": 0.65, "RB": 1.00, "WR": 1.00, "TE": 1.70, "K": 0.30, "DST": 0.30},
    "Late QB":      {"QB": 0.25, "RB": 1.25, "WR": 1.25, "TE": 0.90, "K": 0.30, "DST": 0.30},
    "Balanced BPA": {"QB": 1.00, "RB": 1.00, "WR": 1.00, "TE": 1.00, "K": 0.50, "DST": 0.50},
}

def ai_pick(available: list, team_roster: list, strategy: dict) -> dict:
    """Select best player using strategy-weighted VOR."""
    weights = strategy
    pos_counts = {p["pos"]: pos_counts.get(p["pos"], 0) + 1 for p in team_roster}
    pos_needs = {"QB": 3, "RB": 5, "WR": 5, "TE": 2, "K": 2, "DST": 2}
    best, best_score = None, float("-inf")

    for player in available[:60]:  # scan top 60 by VOR
        score = player["vor"] * weights.get(player["pos"], 1.0)

        # Need bonus: +15% if roster slot open
        if pos_counts.get(player["pos"], 0) < pos_needs[player["pos"]]:
            score *= 1.15
        else:
            score *= 0.45  # heavy penalty if position full

        # Scarcity check: positional urgency
        remaining = sum(1 for p in available[:40] if p["pos"] == player["pos"])
        if remaining <= 3:
            score *= 1.35
        elif remaining <= 6:
            score *= 1.12

        # Behavioral jitter: ±8% randomization
        import random
        score *= (0.92 + random.random() * 0.16)

        if score > best_score:
            best, best_score = player, score

    return best</pre>
  </details>

  <details>
    <summary>&#x1F40D; Snake Draft Order Generator (Python)</summary>
    <pre>
# ── Snake Draft Order ────────────────────────────────────────────
# In a snake draft, odd rounds go 1→12, even rounds go 12→1.
# This creates the "snake" pattern that ensures fairness.

def build_draft_queue(num_teams: int = 12, num_rounds: int = 19) -> list[dict]:
    """
    Returns a flat list of {round, pick_in_round, team_idx}
    in snake order across all rounds.
    """
    queue = []
    for r in range(num_rounds):
        order = list(range(num_teams))
        if r % 2 == 1:          # even rounds (0-indexed) reverse
            order = order[::-1]
        for pick_pos, team_idx in enumerate(order):
            queue.append({
                "round":         r,
                "pick_in_round": pick_pos,
                "team_idx":      team_idx,
                "overall_pick":  r * num_teams + pick_pos + 1,
            })
    return queue

# Example output (12-team, first 2 rounds):
# Round 1: teams 0,1,2,...,11 (picks 1–12)
# Round 2: teams 11,10,9,...,0 (picks 13–24)
# Team 0 gets picks 1 and 24 (gap = 23)
# Team 11 gets picks 12 and 13 (back-to-back)</pre>
  </details>

  <details>
    <summary>&#x1F4CA; Post-Draft Grade Analysis (Python)</summary>
    <pre>
# ── Post-Draft Grading Algorithm ──────────────────────────────────
# Grades each team on four dimensions then assigns A+ through D.

def grade_team(roster: list, all_teams: list, league_size: int = 12) -> dict:
    by_pos = {}
    for p in roster:
        by_pos.setdefault(p["pos"], []).append(p)
    for pos in by_pos:
        by_pos[pos].sort(key=lambda x: x["projected_pts"], reverse=True)

    # 1. Starter Projected Points
    starter_pts = 0
    if by_pos.get("QB"):  starter_pts += by_pos["QB"][0]["projected_pts"]
    for i in range(min(2, len(by_pos.get("RB", [])))):
        starter_pts += by_pos["RB"][i]["projected_pts"]
    for i in range(min(2, len(by_pos.get("WR", [])))):
        starter_pts += by_pos["WR"][i]["projected_pts"]
    if by_pos.get("TE"):  starter_pts += by_pos["TE"][0]["projected_pts"]
    # FLEX: best remaining RB/WR/TE
    flex = sorted(
        [p for pos in ["RB","WR","TE"] for p in by_pos.get(pos,[])[2:]],
        key=lambda x: x["projected_pts"], reverse=True
    )
    if flex: starter_pts += flex[0]["projected_pts"]
    if by_pos.get("K"):   starter_pts += by_pos["K"][0]["projected_pts"]
    if by_pos.get("DST"): starter_pts += by_pos["DST"][0]["projected_pts"]

    # 2. Bye Week Concentration Penalty
    bye_counts = {}
    for p in roster:
        bye_counts[p["bye"]] = bye_counts.get(p["bye"], 0) + 1
    bye_penalty = sum(1 for count in bye_counts.values() if count >= 3)

    # 3. Rank among all teams, assign grade
    all_starter_pts = sorted(
        [compute_starter_pts(t) for t in all_teams], reverse=True
    )
    rank = all_starter_pts.index(starter_pts) + 1
    grade_map = ["A+","A","A","A-","B+","B","B","B-","C+","C","C-","D"]
    grade_idx = min(rank - 1 + bye_penalty, len(grade_map) - 1)

    return {
        "grade":        grade_map[grade_idx],
        "rank":         rank,
        "starter_pts":  round(starter_pts),
        "bye_conflicts": bye_penalty,
        "total_vor":    round(sum(p["vor"] for p in roster)),
    }</pre>
  </details>

</div>
</section>

<!-- ═══ ABOUT ═══ -->
<section id="nd-about">
<div class="nd-about">
  <div class="nd-about-card">
    <h3>&#x1F3C8; Built for the Portfolio</h3>
    <p>This demo is part of the <strong>7-Ideations Framework</strong> &mdash; a portfolio approach that walks from narrative to live demo to classroom to production code. Every pick in the simulator reflects a real algorithmic decision: VOR ranking, strategy-weighted AI, scarcity detection, and post-draft analytics.</p>
    <p style="font-size:.75rem;color:var(--nd-muted);margin-bottom:1.2rem">The most modern resume for the most modern city on earth.</p>
    <button class="nd-share-btn" id="ndShareBtn" onclick="ndShareDemo()">
      <i class="fas fa-share-alt me-1"></i> Share This Demo
    </button>
  </div>
</div>
</section>

{% endblock content %}
''')
