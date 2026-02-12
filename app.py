import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Retro Space Shooter", layout="wide")
st.title("🕹️ Retro Space Shooter")
st.caption("Blast enemy waves across 5 levels. Use ◀ ▶ or A/D to move, SPACE to shoot, and ENTER to restart after game over.")

components.html(
    """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    html, body {
      margin: 0;
      background: radial-gradient(circle at top, #111133 0%, #05050f 50%, #010104 100%);
      color: #7ef9ff;
      font-family: 'Courier New', monospace;
      overflow: hidden;
    }
    #game-wrap {
      width: 100vw;
      height: 90vh;
      position: relative;
    }
    #hud {
      position: absolute;
      top: 12px;
      left: 12px;
      z-index: 2;
      font-size: 16px;
      line-height: 1.4;
      text-shadow: 0 0 8px #00e5ff;
      pointer-events: none;
    }
    #overlay {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      z-index: 3;
      color: #ff66c4;
      font-size: 22px;
      text-shadow: 0 0 12px #ff66c4;
      pointer-events: none;
      opacity: 0;
      transition: opacity 220ms ease;
      white-space: pre-line;
    }
  </style>
</head>
<body>
  <div id="game-wrap">
    <div id="hud">Score: 0<br/>Lives: 3<br/>Level: 1/5</div>
    <div id="overlay"></div>
  </div>

  <script type="module">
    import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js';

    const wrap = document.getElementById('game-wrap');
    const hud = document.getElementById('hud');
    const overlay = document.getElementById('overlay');

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x03030a, 20, 80);

    const camera = new THREE.PerspectiveCamera(65, wrap.clientWidth / wrap.clientHeight, 0.1, 200);
    camera.position.set(0, 4.5, 12);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(wrap.clientWidth, wrap.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x020207, 1);
    wrap.appendChild(renderer.domElement);

    const ambient = new THREE.AmbientLight(0x8090ff, 0.7);
    scene.add(ambient);

    const point = new THREE.PointLight(0x55f0ff, 1.3, 40);
    point.position.set(0, 7, 8);
    scene.add(point);

    const stars = new THREE.Group();
    const starGeo = new THREE.SphereGeometry(0.03, 5, 5);
    const starMat = new THREE.MeshBasicMaterial({ color: 0x7ef9ff });
    for (let i = 0; i < 280; i++) {
      const s = new THREE.Mesh(starGeo, starMat);
      s.position.set((Math.random() - 0.5) * 35, Math.random() * 20 - 4, -Math.random() * 90);
      stars.add(s);
    }
    scene.add(stars);

    const player = new THREE.Group();
    const body = new THREE.Mesh(
      new THREE.ConeGeometry(0.45, 1.6, 6),
      new THREE.MeshStandardMaterial({ color: 0xff66c4, emissive: 0x4f0f34, metalness: 0.2, roughness: 0.5 })
    );
    body.rotation.x = Math.PI / 2;
    player.add(body);

    const wingGeo = new THREE.BoxGeometry(1.3, 0.08, 0.35);
    const wingMat = new THREE.MeshStandardMaterial({ color: 0x84d8ff, emissive: 0x102c42 });
    const wings = new THREE.Mesh(wingGeo, wingMat);
    wings.position.set(0, -0.05, 0.2);
    player.add(wings);

    player.position.set(0, -2.8, 0);
    scene.add(player);

    const keys = new Set();
    const bullets = [];
    const enemies = [];
    const sparks = [];

    const maxLevels = 5;
    const state = {
      score: 0,
      lives: 3,
      level: 1,
      levelKills: 0,
      targetKills: 8,
      enemySpeed: 0.035,
      enemySpawnMs: 950,
      bulletCooldown: 0,
      gameOver: false,
      win: false,
      spawnClock: 0,
      pulseClock: 0,
    };

    function updateHud() {
      hud.innerHTML = `Score: ${state.score}<br/>Lives: ${state.lives}<br/>Level: ${state.level}/${maxLevels}`;
    }

    function showOverlay(text, visible = true) {
      overlay.textContent = text;
      overlay.style.opacity = visible ? '1' : '0';
    }

    function makeEnemy() {
      const palette = [0xff3366, 0xff7b00, 0xfff200, 0x96ff00, 0x2df7ff];
      const color = palette[(state.level - 1) % palette.length];
      const enemy = new THREE.Mesh(
        new THREE.IcosahedronGeometry(0.48 + state.level * 0.03, 0),
        new THREE.MeshStandardMaterial({ color, emissive: color * 0.18, metalness: 0.25, roughness: 0.35 })
      );
      enemy.position.set((Math.random() - 0.5) * 10, 3.8, -Math.random() * 6);
      enemy.userData.spin = (Math.random() * 0.04 + 0.01) * (Math.random() > 0.5 ? 1 : -1);
      scene.add(enemy);
      enemies.push(enemy);
    }

    function shoot() {
      const b = new THREE.Mesh(
        new THREE.CylinderGeometry(0.045, 0.045, 0.42, 8),
        new THREE.MeshBasicMaterial({ color: 0x7ef9ff })
      );
      b.rotation.x = Math.PI / 2;
      b.position.copy(player.position);
      b.position.y += 0.4;
      scene.add(b);
      bullets.push(b);
    }

    function explode(pos, color = 0xff66c4) {
      for (let i = 0; i < 10; i++) {
        const p = new THREE.Mesh(
          new THREE.SphereGeometry(0.06, 4, 4),
          new THREE.MeshBasicMaterial({ color })
        );
        p.position.copy(pos);
        p.userData.vx = (Math.random() - 0.5) * 0.24;
        p.userData.vy = (Math.random() - 0.5) * 0.24;
        p.userData.vz = (Math.random() - 0.5) * 0.24;
        p.userData.life = 32;
        scene.add(p);
        sparks.push(p);
      }
    }

    function removeMesh(arr, i) {
      scene.remove(arr[i]);
      arr[i].geometry.dispose();
      arr[i].material.dispose();
      arr.splice(i, 1);
    }

    function levelUp() {
      if (state.level >= maxLevels) {
        state.win = true;
        state.gameOver = true;
        showOverlay(`YOU WIN!\nFinal Score: ${state.score}\nPress ENTER to play again`);
        return;
      }

      state.level += 1;
      state.levelKills = 0;
      state.targetKills = 8 + state.level * 2;
      state.enemySpeed += 0.015;
      state.enemySpawnMs = Math.max(350, state.enemySpawnMs - 120);
      showOverlay(`LEVEL ${state.level}`, true);
      setTimeout(() => {
        if (!state.gameOver) showOverlay('', false);
      }, 900);
      updateHud();
    }

    function resetGame() {
      while (bullets.length) removeMesh(bullets, 0);
      while (enemies.length) removeMesh(enemies, 0);
      while (sparks.length) removeMesh(sparks, 0);
      state.score = 0;
      state.lives = 3;
      state.level = 1;
      state.levelKills = 0;
      state.targetKills = 8;
      state.enemySpeed = 0.035;
      state.enemySpawnMs = 950;
      state.bulletCooldown = 0;
      state.spawnClock = 0;
      state.gameOver = false;
      state.win = false;
      player.position.x = 0;
      updateHud();
      showOverlay('LEVEL 1', true);
      setTimeout(() => showOverlay('', false), 800);
    }

    function loseLife() {
      state.lives -= 1;
      explode(player.position, 0xff4477);
      updateHud();
      if (state.lives <= 0) {
        state.gameOver = true;
        showOverlay(`GAME OVER\nScore: ${state.score}\nPress ENTER to retry`);
      }
    }

    document.addEventListener('keydown', (e) => {
      const key = e.key.toLowerCase();
      keys.add(key);
      if (key === 'enter' && state.gameOver) {
        resetGame();
      }
    });

    document.addEventListener('keyup', (e) => keys.delete(e.key.toLowerCase()));

    function animate(ts) {
      requestAnimationFrame(animate);

      const delta = 16;
      state.pulseClock += delta * 0.001;

      stars.children.forEach((s) => {
        s.position.z += 0.15 + state.level * 0.02;
        if (s.position.z > 5) {
          s.position.z = -90;
          s.position.x = (Math.random() - 0.5) * 35;
          s.position.y = Math.random() * 20 - 4;
        }
      });

      if (!state.gameOver) {
        const speed = 0.18;
        if (keys.has('arrowleft') || keys.has('a')) player.position.x -= speed;
        if (keys.has('arrowright') || keys.has('d')) player.position.x += speed;
        player.position.x = Math.max(-5.2, Math.min(5.2, player.position.x));

        state.bulletCooldown -= delta;
        if ((keys.has(' ') || keys.has('space')) && state.bulletCooldown <= 0) {
          shoot();
          state.bulletCooldown = 210;
        }

        state.spawnClock += delta;
        if (state.spawnClock >= state.enemySpawnMs) {
          state.spawnClock = 0;
          makeEnemy();
        }
      }

      for (let i = bullets.length - 1; i >= 0; i--) {
        const b = bullets[i];
        b.position.y += 0.3;
        if (b.position.y > 6) removeMesh(bullets, i);
      }

      for (let i = enemies.length - 1; i >= 0; i--) {
        const e = enemies[i];
        if (!state.gameOver) {
          e.position.y -= state.enemySpeed;
          e.rotation.x += e.userData.spin;
          e.rotation.y += e.userData.spin * 1.25;
        }

        if (e.position.y < -3.8) {
          removeMesh(enemies, i);
          if (!state.gameOver) loseLife();
          continue;
        }

        for (let j = bullets.length - 1; j >= 0; j--) {
          if (e.position.distanceTo(bullets[j].position) < 0.62) {
            const hitPos = e.position.clone();
            removeMesh(enemies, i);
            removeMesh(bullets, j);
            explode(hitPos, 0x7ef9ff);
            state.score += 10 * state.level;
            state.levelKills += 1;
            updateHud();
            if (state.levelKills >= state.targetKills) levelUp();
            break;
          }
        }
      }

      for (let i = sparks.length - 1; i >= 0; i--) {
        const p = sparks[i];
        p.position.x += p.userData.vx;
        p.position.y += p.userData.vy;
        p.position.z += p.userData.vz;
        p.userData.life -= 1;
        p.material.opacity = Math.max(0, p.userData.life / 32);
        p.material.transparent = true;
        if (p.userData.life <= 0) removeMesh(sparks, i);
      }

      point.intensity = 1.1 + Math.sin(state.pulseClock * 2.2) * 0.2;
      player.rotation.z = Math.sin(state.pulseClock * 6) * 0.03;

      renderer.render(scene, camera);
    }

    window.addEventListener('resize', () => {
      camera.aspect = wrap.clientWidth / wrap.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(wrap.clientWidth, wrap.clientHeight);
    });

    showOverlay('LEVEL 1', true);
    setTimeout(() => showOverlay('', false), 800);
    animate();
  </script>
</body>
</html>
    """,
    height=760,
)
