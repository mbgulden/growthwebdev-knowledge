---
type: Code
title: "Darius Star - Fighter Jet Game.html"
description: Early Darius Star prototype source code — preserved for historical reference. Modern game uses modular JS in darius-star repo.
resource: okf/projects/darius-star/storyline/darius-star-fighter-jet-game-html.md
tags: [darius-star, prototype, source-code, historical]
timestamp: 2026-06-19T12:30:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/storyline/darius-star-fighter-jet-game.html
last_verified: 2026-08-19
verified_by: kai
status: historical
migrated_from: "Google Drive: mbgulden@gmail.com > Darius Star - Fighter Jet Game.html"
google_doc_id: 10AQEp1Gi9ZH_DpaMUrGn-O4A_gRBzUWg-p00mX_3ExM
modified_in_drive: 2026-06-08T15:28:51.044Z
migrated_from_repo: mbgulden/darius-star
---
## Historical Note

This is an **early prototype** of Darius Star (originally called "Fighter Jet Game"). It predates the modular JS architecture that the current game uses.

**Source code preserved below for historical reference. The current canonical Darius Star implementation lives in the [darius-star repo](https://github.com/mbgulden/darius-star).**

---

```html
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Darius Star: Cyber Coelacanth</title>

    <style>

        body {

            margin: 0;

            padding: 0;

            background-color: #050510;

            color: #fff;

            font-family: 'Courier New', Courier, monospace;

            display: flex;

            flex-direction: column;

            align-items: center;

            justify-content: center;

            min-height: 100vh;

            overflow: hidden;

        }


        h1 {

            margin: 5px 0;

            font-size: 24px;

            color: #00ffff;

            text-shadow: 0 0 10px #00ffff, 0 0 20px #0000ff;

            letter-spacing: 2px;

        }


        #game-container {

            position: relative;

            border: 4px solid #3a3a5a;

            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);

            background-color: #000;

            image-rendering: pixelated;

        }


        canvas {

            display: block;

            background: #000;

        }


        .instructions {

            margin-top: 10px;

            font-size: 14px;

            color: #8a8a9f;

            text-align: center;

            max-width: 800px;

            line-height: 1.4;

        }


        .keys {

            color: #00ffff;

            font-weight: bold;

        }


        #controls-overlay {

            position: absolute;

            top: 10px;

            right: 10px;

            background: rgba(10, 10, 30, 0.7);

            padding: 8px;

            border-radius: 4px;

            border: 1px solid #00ffff;

            font-size: 12px;

            pointer-events: none;

        }

    </style>

</head>

<body>


    <h1>DARIUS STAR: CYBER COELACANTH</h1>

    <div id="game-container">

        <canvas id="gameCanvas" width="800" height="450"></canvas>

        <div id="controls-overlay">

            <div style="color: #ff0055; font-weight: bold; margin-bottom: 4px;">SYSTEM STATUS</div>

            <div>SHIELD: <span id="ui-shield" style="color: #00ff00;">100%</span></div>

            <div>WEAPON: <span id="ui-weapon" style="color: #ffff00;">LVL 1</span></div>

            <div>SCORE: <span id="ui-score" style="color: #00ffff;">0</span></div>

        </div>

    </div>


    <div class="instructions">

        <span class="keys">W, A, S, D</span> or <span class="keys">ARROW KEYS</span> to Move | 

        <span class="keys">SPACEBAR</span> or <span class="keys">J</span> to Fire | 

        <span class="keys">P</span> to Pause

        <br>

        <span style="color: #ff0055;">Red Orbs</span> upgrade primary weapons. <span style="color: #00ff55;">Green Orbs</span> restore Shields. Reaching 2,000 points triggers the Boss Battle!

    </div>


    <script>

        // --- Web Audio Synthesizer ---

        let audioCtx = null;

        function initAudio() {

            if (!audioCtx) {

                audioCtx = new (window.AudioContext || window.webkitAudioContext)();

            }

            if (audioCtx.state === 'suspended') {

                audioCtx.resume();

            }

        }


        function playSound(type) {

            if (!audioCtx) return;

            try {

                const osc = audioCtx.createOscillator();

                const gain = audioCtx.createGain();

                osc.connect(gain);

                gain.connect(audioCtx.destination);


                if (type === 'shoot') {

                    osc.type = 'sawtooth';

                    osc.frequency.setValueAtTime(500, audioCtx.currentTime);

                    osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + 0.12);

                    gain.gain.setValueAtTime(0.08, audioCtx.currentTime);

                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.12);

                    osc.start();

                    osc.stop(audioCtx.currentTime + 0.12);

                } else if (type === 'hit') {

                    osc.type = 'triangle';

                    osc.frequency.setValueAtTime(140, audioCtx.currentTime);

                    osc.frequency.exponentialRampToValueAtTime(30, audioCtx.currentTime + 0.1);

                    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);

                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1);

                    osc.start();

                    osc.stop(audioCtx.currentTime + 0.1);

                } else if (type === 'explosion') {

                    osc.type = 'sawtooth';

                    osc.frequency.setValueAtTime(80, audioCtx.currentTime);

                    osc.frequency.exponentialRampToValueAtTime(10, audioCtx.currentTime + 0.45);

                    gain.gain.setValueAtTime(0.25, audioCtx.currentTime);

                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.45);

                    osc.start();

                    osc.stop(audioCtx.currentTime + 0.45);

                } else if (type === 'powerup') {

                    osc.type = 'sine';

                    osc.frequency.setValueAtTime(280, audioCtx.currentTime);

                    osc.frequency.linearRampToValueAtTime(520, audioCtx.currentTime + 0.08);

                    osc.frequency.linearRampToValueAtTime(850, audioCtx.currentTime + 0.2);

                    gain.gain.setValueAtTime(0.12, audioCtx.currentTime);

                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);

                    osc.start();

                    osc.stop(audioCtx.currentTime + 0.2);

                } else if (type === 'siren') {

                    osc.type = 'sawtooth';

                    osc.frequency.setValueAtTime(350, audioCtx.currentTime);

                    osc.frequency.linearRampToValueAtTime(450, audioCtx.currentTime + 0.2);

                    osc.frequency.linearRampToValueAtTime(350, audioCtx.currentTime + 0.4);

                    gain.gain.setValueAtTime(0.06, audioCtx.currentTime);

                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);

                    osc.start();

                    osc.stop(audioCtx.currentTime + 0.4);

                } else if (type === 'laser_charge') {

                    osc.type = 'sine';

                    osc.frequency.setValueAtTime(100, audioCtx.currentTime);

                    osc.frequency.exponentialRampToValueAtTime(1000, audioCtx.currentTime + 1.2);

                    gain.gain.setValueAtTime(0.05, audioCtx.currentTime);

                    gain.gain.exponentialRampToValueAtTime(0.1, audioCtx.currentTime + 1.2);

                    osc.start();

                    osc.stop(audioCtx.currentTime + 1.2);

                } else if (type === 'laser_fire') {

                    osc.type = 'sawtooth';

                    osc.frequency.setValueAtTime(120, audioCtx.currentTime);

                    osc.frequency.linearRampToValueAtTime(80, audioCtx.currentTime + 1.5);

                    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);

                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 1.5);

                    osc.start();

                    osc.stop(audioCtx.currentTime + 1.5);

                }

            } catch (e) {

                console.log("Audio play blocked/failed:", e);

            }

        }


        // --- Game Setup ---

        const canvas = document.getElementById('gameCanvas');

        const ctx = canvas.getContext('2d');


        const uiShield = document.getElementById('ui-shield');

        const uiWeapon = document.getElementById('ui-weapon');

        const uiScore = document.getElementById('ui-score');


        // Game state variables

        let score = 0;

        let gameOver = false;

        let gameWon = false;

        let paused = false;

        let lastTime = 0;

        let gameTime = 0;

        let bossSpawned = false;

        let sirenTimer = 0;


        // Keys pressed

        const keys = {};

        window.addEventListener('keydown', e => {

            initAudio();

            if (e.key === 'p' || e.key === 'P') {

                paused = !paused;

            }

            keys[e.key] = true;

            // Prevent scrolling on space / arrow keys

            if (['Space', ' ', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].indexOf(e.key) > -1) {

                e.preventDefault();

            }

        });

        window.addEventListener('keyup', e => {

            keys[e.key] = false;

        });


        // --- Player Ship Class ---

        class Player {

            constructor() {

                this.x = 80;

                this.y = canvas.height / 2;

                this.width = 40;

                this.height = 20;

                this.speed = 220; // px/sec

                this.shieldMax = 100;

                this.shield = 100;

                this.weaponLevel = 1;

                this.shootCooldown = 0.15; // seconds

                this.shootTimer = 0;

                this.color = '#00ffff';

                this.invulnerable = 0; // seconds

            }


            update(dt) {

                if (this.invulnerable > 0) {

                    this.invulnerable -= dt;

                }


                // Movement

                let dx = 0;

                let dy = 0;

                if (keys['w'] || keys['W'] || keys['ArrowUp']) dy -= 1;

                if (keys['s'] || keys['S'] || keys['ArrowDown']) dy += 1;

                if (keys['a'] || keys['A'] || keys['ArrowLeft']) dx -= 1;

                if (keys['d'] || keys['D'] || keys['ArrowRight']) dx += 1;


                // Normalize vector for diagonals

                if (dx !== 0 && dy !== 0) {

                    dx *= 0.7071;

                    dy *= 0.7071;

                }


                this.x += dx * this.speed * dt;

                this.y += dy * this.speed * dt;


                // Keep inside canvas boundary

                if (this.x < 10) this.x = 10;

                if (this.x > canvas.width - this.width - 10) this.x = canvas.width - this.width - 10;

                if (this.y < 10) this.y = 10;

                if (this.y > canvas.height - this.height - 10) this.y = canvas.height - this.height - 10;


                // Shooting

                if (this.shootTimer > 0) {

                    this.shootTimer -= dt;

                }


                if ((keys[' '] || keys['j'] || keys['J']) && this.shootTimer <= 0) {

                    this.shoot();

                    this.shootTimer = this.shootCooldown;

                }

            }


            shoot() {

                playSound('shoot');

                const bulletSpeed = 550;

                const bulletSize = 4;


                if (this.weaponLevel === 1) {

                    // Level 1: Straight Single Bullet

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height/2, bulletSpeed, 0, '#00ffff', bulletSize));

                } else if (this.weaponLevel === 2) {

                    // Level 2: Double Bullet

                    bullets.push(new Bullet(this.x + this.width, this.y + 4, bulletSpeed, 0, '#00ffaa', bulletSize + 1));

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height - 4, bulletSpeed, 0, '#00ffaa', bulletSize + 1));

                } else if (this.weaponLevel === 3) {

                    // Level 3: Triple Wide Spread

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height/2, bulletSpeed, 0, '#ffff00', bulletSize + 1));

                    bullets.push(new Bullet(this.x + this.width, this.y + 2, bulletSpeed, -100, '#ffff00', bulletSize));

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height - 2, bulletSpeed, 100, '#ffff00', bulletSize));

                } else if (this.weaponLevel === 4) {

                    // Level 4: Heavy Pulsar / Wave Beam

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height/2, bulletSpeed, 0, '#ff00ff', 12, true));

                    bullets.push(new Bullet(this.x + this.width, this.y + 2, bulletSpeed - 50, -120, '#00ffff', bulletSize));

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height - 2, bulletSpeed - 50, 120, '#00ffff', bulletSize));

                } else {

                    // Level 5 (MAX): Supreme Nova Fire

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height/2, bulletSpeed + 50, 0, '#ffffff', 14, true));

                    bullets.push(new Bullet(this.x + this.width, this.y + 2, bulletSpeed, -160, '#ff00aa', bulletSize + 2));

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height - 2, bulletSpeed, 160, '#ff00aa', bulletSize + 2));

                    bullets.push(new Bullet(this.x + this.width, this.y + 4, bulletSpeed - 80, -300, '#ffff00', bulletSize + 1));

                    bullets.push(new Bullet(this.x + this.width, this.y + this.height - 4, bulletSpeed - 80, 300, '#ffff00', bulletSize + 1));

                }

            }


            takeDamage(amt) {

                if (this.invulnerable > 0) return;

                this.shield -= amt;

                this.invulnerable = 0.8; // 0.8 seconds invuln

                playSound('hit');

                createExplosion(this.x + this.width/2, this.y + this.height/2, '#ffaa00', 8);


                if (this.shield <= 0) {

                    this.shield = 0;

                    gameOver = true;

                    playSound('explosion');

                    createExplosion(this.x, this.y, '#ff0000', 40);

                }

            }


            draw() {

                if (this.invulnerable > 0 && Math.floor(this.invulnerable * 15) % 2 === 0) {

                    return; // Flashing effect

                }


                ctx.save();

                ctx.translate(this.x, this.y);


                // Main Thruster Jet Flame

                const flameLength = 10 + Math.random() * 15;

                const gradient = ctx.createLinearGradient(-flameLength, this.height/2, 0, this.height/2);

                gradient.addColorStop(0, 'rgba(255, 0, 0, 0)');

                gradient.addColorStop(0.5, '#ff7700');

                gradient.addColorStop(1, '#ffdd00');

                ctx.fillStyle = gradient;

                ctx.beginPath();

                ctx.moveTo(0, 5);

                ctx.lineTo(-flameLength, this.height/2);

                ctx.lineTo(0, this.height - 5);

                ctx.closePath();

                ctx.fill();


                // Draw retro fuselage (Silver / metallic body, blue nose)

                ctx.fillStyle = '#8a9fbc'; // Silver fuselage

                ctx.beginPath();

                ctx.moveTo(0, 4);

                ctx.lineTo(25, 4);

                ctx.lineTo(40, this.height / 2); // Nose cone

                ctx.lineTo(25, this.height - 4);

                ctx.lineTo(0, this.height - 4);

                ctx.closePath();

                ctx.fill();


                // Wings

                ctx.fillStyle = '#3a5a8a'; // Darker wing panels

                ctx.beginPath();

                ctx.moveTo(5, 4);

                ctx.lineTo(12, -6);

                ctx.lineTo(22, 4);

                ctx.closePath();

                ctx.fill();


                ctx.beginPath();

                ctx.moveTo(5, this.height - 4);

                ctx.lineTo(12, this.height + 6);

                ctx.lineTo(22, this.height - 4);

                ctx.closePath();

                ctx.fill();


                // Cockpit canopy (cyan)

                ctx.fillStyle = '#00ffff';

                ctx.beginPath();

                ctx.moveTo(20, 6);

                ctx.lineTo(28, 6);

                ctx.lineTo(34, this.height/2);

                ctx.lineTo(28, this.height - 6);

                ctx.lineTo(20, this.height - 6);

                ctx.closePath();

                ctx.fill();


                // Weapon Pod (laser emitter)

                ctx.fillStyle = '#ff0055';

                ctx.fillRect(10, this.height/2 - 3, 12, 6);


                // Shield forcefield bubble (faint cyan outline if shielded)

                if (this.weaponLevel >= 4) {

                    ctx.strokeStyle = 'rgba(0, 255, 255, 0.4)';

                    ctx.lineWidth = 2;

                    ctx.beginPath();

                    ctx.arc(this.width/2, this.height/2, 28, 0, Math.PI * 2);

                    ctx.stroke();

                }


                ctx.restore();

            }

        }


        // --- Bullet Class ---

        class Bullet {

            constructor(x, y, vx, vy, color, size = 4, isWave = false) {

                this.x = x;

                this.y = y;

                this.vx = vx;

                this.vy = vy;

                this.color = color;

                this.size = size;

                this.isWave = isWave;

                this.age = 0;

            }


            update(dt) {

                this.x += this.vx * dt;

                this.y += this.vy * dt;

                this.age += dt;


                if (this.isWave) {

                    // Sinusoidal wave pattern

                    this.y += Math.sin(this.age * 22) * 4;

                }

            }


            draw() {

                ctx.fillStyle = this.color;

                if (this.isWave) {

                    ctx.shadowColor = this.color;

                    ctx.shadowBlur = 10;

                    ctx.beginPath();

                    ctx.arc(this.x, this.y, this.size, 0, Math.PI*2);

                    ctx.fill();

                    ctx.shadowBlur = 0;

                } else {

                    ctx.fillRect(this.x - this.size, this.y - 2, this.size * 2, 4);

                }

            }

        }


        // --- Enemy Bullet Class ---

        class EnemyBullet {

            constructor(x, y, vx, vy) {

                this.x = x;

                this.y = y;

                this.vx = vx;

                this.vy = vy;

                this.color = '#ff3300';

                this.size = 5;

            }


            update(dt) {

                this.x += this.vx * dt;

                this.y += this.vy * dt;

            }


            draw() {

                ctx.fillStyle = this.color;

                ctx.beginPath();

                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);

                ctx.fill();

            }

        }


        // --- Enemy Ship Classes ---

        class Enemy {

            constructor(type) {

                this.type = type; // 'scout', 'interceptor', 'heavy', 'boss_minion'

                this.x = canvas.width + 50;

                this.y = 50 + Math.random() * (canvas.height - 100);

                this.width = 30;

                this.height = 30;

                this.age = 0;


                // Configure stats by type

                if (type === 'scout') {

                    this.speed = 150;

                    this.hp = 1;

                    this.scoreValue = 100;

                    this.color = '#ff5500';

                    this.startY = this.y;

                } else if (type === 'interceptor') {

                    this.speed = 280;

                    this.hp = 1;

                    this.scoreValue = 150;

                    this.color = '#ff0055';

                } else if (type === 'heavy') {

                    this.speed = 80;

                    this.hp = 4;

                    this.scoreValue = 300;

                    this.color = '#9a33cc';

                    this.shootCooldown = 1.2 + Math.random() * 0.8;

                    this.shootTimer = this.shootCooldown;

                } else { // boss minion

                    this.speed = 180;

                    this.hp = 2;

                    this.scoreValue = 50;

                    this.color = '#33cc55';

                }

            }


            update(dt) {

                this.age += dt;


                if (this.type === 'scout') {

                    // Fly in a sine wave path

                    this.x -= this.speed * dt;

                    this.y = this.startY + Math.sin(this.age * 5) * 60;

                } else if (this.type === 'interceptor') {

                    // Charge straight left rapidly

                    this.x -= this.speed * dt;

                } else if (this.type === 'heavy') {

                    // Slowly drift left and shoot at the player

                    this.x -= this.speed * dt;

                    this.shootTimer -= dt;

                    if (this.shootTimer <= 0) {

                        this.shoot();

                        this.shootTimer = this.shootCooldown;

                    }

                } else if (this.type === 'boss_minion') {

                    // Scurry quickly from boss down/up

                    this.x -= this.speed * dt;

                    this.y += Math.sin(this.age * 8) * 80 * dt;

                }

            }


            shoot() {

                // Vector towards player

                const dx = player.x - this.x;

                const dy = player.y - this.y;

                const dist = Math.sqrt(dx*dx + dy*dy);

                const bulletSpeed = -220; // Towards left/player


                // Shoot simple linear bullet leftward

                enemyBullets.push(new EnemyBullet(this.x, this.y + this.height/2, bulletSpeed, (dy/dist) * 100));

            }


            draw() {

                ctx.save();

                ctx.translate(this.x, this.y);


                // Draw retro enemy ships (organic metal scale look, reminiscent of Darius)

                ctx.fillStyle = this.color;

                

                if (this.type === 'scout') {

                    // Diamond-shaped fish/scout

                    ctx.beginPath();

                    ctx.moveTo(30, 15);

                    ctx.lineTo(10, 0);

                    ctx.lineTo(0, 15);

                    ctx.lineTo(10, 30);

                    ctx.closePath();

                    ctx.fill();

                    // Glowing cyan eye

                    ctx.fillStyle = '#00ffff';

                    ctx.fillRect(8, 10, 4, 4);

                } else if (this.type === 'interceptor') {

                    // Arrowhead structure

                    ctx.beginPath();

                    ctx.moveTo(30, 15);

                    ctx.lineTo(0, 5);

                    ctx.lineTo(10, 15);

                    ctx.lineTo(0, 25);

                    ctx.closePath();

                    ctx.fill();

                    // Red trail flame

                    ctx.fillStyle = '#ff7700';

                    ctx.fillRect(32, 12, 6, 6);

                } else if (this.type === 'heavy') {

                    // Robust heavy armor shell (looks like a crab/trilobite shell)

                    ctx.beginPath();

                    ctx.moveTo(30, 5);

                    ctx.lineTo(10, 0);

                    ctx.lineTo(0, 15);

                    ctx.lineTo(10, 30);

                    ctx.lineTo(30, 25);

                    ctx.lineTo(20, 15);

                    ctx.closePath();

                    ctx.fill();


                    // Shield plating lines

                    ctx.strokeStyle = '#ffffff';

                    ctx.lineWidth = 1;

                    ctx.beginPath();

                    ctx.moveTo(15, 0);

                    ctx.lineTo(15, 30);

                    ctx.stroke();


                    // Cannon glow

                    ctx.fillStyle = '#ff0000';

                    ctx.beginPath();

                    ctx.arc(5, 15, 4, 0, Math.PI*2);

                    ctx.fill();

                } else if (this.type === 'boss_minion') {

                    // Round green metallic scale minion

                    ctx.beginPath();

                    ctx.arc(15, 15, 12, 0, Math.PI*2);

                    ctx.fill();

                    // Sharp fin

                    ctx.fillStyle = '#118833';

                    ctx.beginPath();

                    ctx.moveTo(15, 3);

                    ctx.lineTo(30, -5);

                    ctx.lineTo(22, 15);

                    ctx.closePath();

                    ctx.fill();

                }


                ctx.restore();

            }

        }


        // --- Boss Fighter Class (Cyber Coelacanth) ---

        class Boss {

            constructor() {

                this.x = canvas.width + 100;

                this.y = canvas.height / 2 - 80;

                this.width = 180;

                this.height = 140;

                this.hpMax = 120;

                this.hp = 120;

                this.state = 'intro'; // 'intro', 'idle', 'rage', 'laser_charge', 'laser_fire'

                this.stateTimer = 2;

                this.bobTimer = 0;

                this.shootTimer = 1.0;

                this.laserWarningTimer = 0;

                this.color = '#305080';

                this.shieldColor = '#ff00aa';

            }


            update(dt) {

                this.bobTimer += dt;


                // Handle entry state

                if (this.state === 'intro') {

                    this.x -= 40 * dt; // Slide in slowly

                    if (this.x <= canvas.width - 210) {

                        this.x = canvas.width - 210;

                        this.state = 'idle';

                        this.stateTimer = 3;

                    }

                    return;

                }


                // Vertical hovering float motion

                this.y += Math.sin(this.bobTimer * 2) * 20 * dt;


                // State Machine handling attack loops

                this.stateTimer -= dt;

                if (this.stateTimer <= 0) {

                    // Swap states

                    if (this.state === 'idle') {

                        // Switch to charging laser or rage

                        if (this.hp < this.hpMax / 2 && Math.random() > 0.4) {

                            this.state = 'laser_charge';

                            this.stateTimer = 1.5;

                            playSound('laser_charge');

                        } else {

                            this.state = 'rage';

                            this.stateTimer = 4;

                        }

                    } else if (this.state === 'rage') {

                        this.state = 'idle';

                        this.stateTimer = 3;

                    } else if (this.state === 'laser_charge') {

                        this.state = 'laser_fire';

                        this.stateTimer = 1.8;

                        playSound('laser_fire');

                    } else if (this.state === 'laser_fire') {

                        this.state = 'idle';

                        this.stateTimer = 3;

                    }

                }


                // Regular Shooting Attacks

                this.shootTimer -= dt;

                if (this.shootTimer <= 0) {

                    this.shootAttack();

                    this.shootTimer = this.state === 'rage' ? 0.3 : 0.75;

                }


                // Laser Beam Action (Warning triggers particle effects)

                if (this.state === 'laser_charge') {

                    createExplosion(this.x + 15, this.y + 70, '#00ffff', 3);

                }

            }


            shootAttack() {

                if (this.state === 'idle') {

                    // Front triple fire spread

                    enemyBullets.push(new EnemyBullet(this.x + 10, this.y + 50, -260, -80));

                    enemyBullets.push(new EnemyBullet(this.x + 10, this.y + 70, -280, 0));

                    enemyBullets.push(new EnemyBullet(this.x + 10, this.y + 90, -260, 80));

                } else if (this.state === 'rage') {

                    // Random homing bullet cluster

                    const dy = player.y - (this.y + 70);

                    const dx = player.x - (this.x + 10);

                    const dist = Math.sqrt(dx*dx + dy*dy);

                    enemyBullets.push(new EnemyBullet(this.x + 10, this.y + 70, (dx/dist) * 320, (dy/dist) * 320));


                    // Spawn small minions occasionally during rage

                    if (Math.random() < 0.25 && enemies.length < 5) {

                        enemies.push(new Enemy('boss_minion'));

                    }

                } else if (this.state === 'laser_fire') {

                    // Spits fireballs upwards and downwards to constrain player space

                    enemyBullets.push(new EnemyBullet(this.x + 40, this.y + 20, -180, -150));

                    enemyBullets.push(new EnemyBullet(this.x + 40, this.y + 110, -180, 150));

                }

            }


            takeDamage(amt) {

                this.hp -= amt;

                playSound('hit');

                createExplosion(this.x + Math.random()*120, this.y + Math.random()*100, '#ffffff', 5);


                if (this.hp <= 0) {

                    this.hp = 0;

                    gameWon = true;

                    playSound('explosion');

                    // Huge chain of final explosions

                    for (let i = 0; i < 35; i++) {

                        setTimeout(() => {

                            createExplosion(this.x + Math.random()*150, this.y + Math.random()*120, '#ff3300', 15);

                            playSound('explosion');

                        }, i * 100);

                    }

                }

            }


            draw() {

                ctx.save();

                ctx.translate(this.x, this.y);


                // Laser warning flash or actual Beam Rendering

                if (this.state === 'laser_fire') {

                    // Draw massive beam spanning entire left screen width

                    ctx.shadowColor = '#00ffff';

                    ctx.shadowBlur = 25;

                    const bGrd = ctx.createLinearGradient(0, 0, 0, 140);

                    bGrd.addColorStop(0, 'rgba(0, 255, 255, 0.2)');

                    bGrd.addColorStop(0.4, '#ffffff');

                    bGrd.addColorStop(0.5, '#00ffff');

                    bGrd.addColorStop(0.6, '#ffffff');

                    bGrd.addColorStop(1, 'rgba(0, 255, 255, 0.2)');

                    ctx.fillStyle = bGrd;

                    ctx.fillRect(-this.x, 50, this.x + 20, 40);

                    ctx.shadowBlur = 0;

                }


                // Boss Metallic scales and segmented body

                // Draw Tail Fins

                ctx.fillStyle = '#ff3366';

                ctx.beginPath();

                ctx.moveTo(140, 70);

                ctx.lineTo(190, 20);

                ctx.lineTo(165, 70);

                ctx.lineTo(190, 120);

                ctx.closePath();

                ctx.fill();


                // Upper Dorsal Spikes / Fins

                ctx.fillStyle = '#ff3366';

                for (let i = 0; i < 3; i++) {

                    ctx.beginPath();

                    ctx.moveTo(40 + i*30, 25);

                    ctx.lineTo(65 + i*30, -15);

                    ctx.lineTo(80 + i*30, 25);

                    ctx.closePath();

                    ctx.fill();

                }


                // Bottom Fins

                for (let i = 0; i < 2; i++) {

                    ctx.beginPath();

                    ctx.moveTo(60 + i*40, 115);

                    ctx.lineTo(80 + i*40, 145);

                    ctx.lineTo(95 + i*40, 115);

                    ctx.closePath();

                    ctx.fill();

                }


                // Segmented Main Steel Shell (Fish scales)

                ctx.fillStyle = this.color;

                ctx.fillRect(30, 25, 120, 90);


                ctx.fillStyle = '#4a6fa5';

                for (let col = 0; col < 4; col++) {

                    for (let row = 0; row < 3; row++) {

                        ctx.fillStyle = (col + row) % 2 === 0 ? '#406090' : '#284068';

                        ctx.fillRect(35 + col*28, 30 + row*26, 25, 22);

                    }

                }


                // Head Section (Heavy steel armored snout)

                ctx.fillStyle = '#1e2d42';

                ctx.beginPath();

                ctx.moveTo(40, 25);

                ctx.lineTo(10, 40);

                ctx.lineTo(0, 70); // Mouth/cannon core

                ctx.lineTo(15, 95);

                ctx.lineTo(40, 115);

                ctx.lineTo(45, 25);

                ctx.closePath();

                ctx.fill();


                // Glowing Eye

                ctx.fillStyle = this.state === 'rage' ? '#ff0000' : '#00ffcc';

                ctx.beginPath();

                ctx.arc(28, 50, 6, 0, Math.PI*2);

                ctx.fill();


                // Cybernetic Cannon Mouthpiece

                ctx.fillStyle = '#ff7700';

                ctx.fillRect(-2, 60, 10, 20);


                // Rage glow pulse

                if (this.state === 'rage') {

                    ctx.strokeStyle = '#ff0055';

                    ctx.lineWidth = 3 + Math.sin(this.bobTimer * 10) * 2;

                    ctx.strokeRect(30, 25, 120, 90);

                }


                ctx.restore();

            }

        }


        // --- PowerUp Class ---

        class PowerUp {

            constructor(x, y, kind) {

                this.x = x;

                this.y = y;

                this.kind = kind; // 'W' = Weapon (red), 'S' = Shield Restore (green)

                this.width = 16;

                this.height = 16;

                this.speed = 100;

                this.bob = 0;

            }


            update(dt) {

                this.x -= this.speed * dt;

                this.bob += dt * 6;

                this.y += Math.sin(this.bob) * 1.2;

            }


            draw() {

                ctx.save();

                ctx.translate(this.x, this.y);


                const color = this.kind === 'W' ? '#ff0055' : '#00ff55';

                ctx.shadowColor = color;

                ctx.shadowBlur = 8;


                // Classic metallic orb shape

                ctx.fillStyle = color;

                ctx.beginPath();

                ctx.arc(8, 8, 8, 0, Math.PI*2);

                ctx.fill();


                // Letter indicator inside orb

                ctx.fillStyle = '#ffffff';

                ctx.font = 'bold 10px monospace';

                ctx.fillText(this.kind, 5, 11);


                ctx.restore();

            }

        }


        // --- Particle Class ---

        class Particle {

            constructor(x, y, color) {

                this.x = x;

                this.y = y;

                this.color = color;

                this.vx = (Math.random() - 0.5) * 250;

                this.vy = (Math.random() - 0.5) * 250;

                this.size = Math.random() * 4 + 1;

                this.alpha = 1.0;

                this.decay = Math.random() * 1.5 + 1.0;

            }


            update(dt) {

                this.x += this.vx * dt;

                this.y += this.vy * dt;

                this.alpha -= this.decay * dt;

            }


            draw() {

                ctx.save();

                ctx.globalAlpha = Math.max(0, this.alpha);

                ctx.fillStyle = this.color;

                ctx.fillRect(this.x, this.y, this.size, this.size);

                ctx.restore();

            }

        }


        // --- Parallax Background Star Class ---

        class Star {

            constructor(layer) {

                this.layer = layer; // 1 (far, slow) to 3 (near, fast)

                this.x = Math.random() * canvas.width;

                this.y = Math.random() * canvas.height;

                this.speed = layer * 45;

                this.size = layer * 0.8;

                this.color = layer === 3 ? '#aaccff' : (layer === 2 ? '#8888aa' : '#444455');

            }


            update(dt) {

                this.x -= this.speed * dt;

                if (this.x < 0) {

                    this.x = canvas.width;

                    this.y = Math.random() * canvas.height;

                }

            }


            draw() {

                ctx.fillStyle = this.color;

                ctx.fillRect(this.x, this.y, this.size, this.size);

            }

        }


        // --- Game Entity Pools ---

        const player = new Player();

        const bullets = [];

        const enemyBullets = [];

        const enemies = [];

        const powerups = [];

        const particles = [];

        const stars = [];


        // Build Stars layers

        for (let i = 0; i < 40; i++) stars.push(new Star(1));

        for (let i = 0; i < 25; i++) stars.push(new Star(2));

        for (let i = 0; i < 12; i++) stars.push(new Star(3));


        let boss = null;

        let enemySpawnTimer = 1.2;


        function createExplosion(x, y, color, count = 12) {

            for (let i = 0; i < count; i++) {

                particles.push(new Particle(x, y, color));

            }

        }


        // --- Core Collision Helper ---

        function checkCollision(rect1, rect2) {

            return rect1.x < rect2.x + rect2.width &&

                   rect1.x + rect1.width > rect2.x &&

                   rect1.y < rect2.y + rect2.height &&

                   rect1.y + rect1.height > rect2.y;

        }


        // --- Game State Controllers ---

        function resetGame() {

            score = 0;

            gameOver = false;

            gameWon = false;

            bossSpawned = false;

            boss = null;

            sirenTimer = 0;

            gameTime = 0;

            player.shield = 100;

            player.weaponLevel = 1;

            player.x = 80;

            player.y = canvas.height / 2;

            bullets.length = 0;

            enemyBullets.length = 0;

            enemies.length = 0;

            powerups.length = 0;

            particles.length = 0;

        }


        // --- Game Main Loop ---

        function loop(timestamp) {

            if (!lastTime) lastTime = timestamp;

            const dt = Math.min((timestamp - lastTime) / 1000, 0.1); // cap dt at 100ms

            lastTime = timestamp;


            if (!paused && !gameOver && !gameWon) {

                gameTime += dt;

                update(dt);

            }


            draw();

            requestAnimationFrame(loop);

        }


        // --- Update Step ---

        function update(dt) {

            // Background Stars

            stars.forEach(star => star.update(dt));


            // Player Ship update

            player.update(dt);


            // Spawn standard enemies before boss

            if (!bossSpawned) {

                enemySpawnTimer -= dt;

                if (enemySpawnTimer <= 0) {

                    const r = Math.random();

                    if (r < 0.45) {

                        enemies.push(new Enemy('scout'));

                    } else if (r < 0.8) {

                        enemies.push(new Enemy('interceptor'));

                    } else {

                        enemies.push(new Enemy('heavy'));

                    }

                    enemySpawnTimer = Math.max(0.6, 1.5 - (score / 15000)); // speed up spawns over time

                }


                // Trigger Boss Battle at 2000 points

                if (score >= 2000) {

                    bossSpawned = true;

                    sirenTimer = 3.0; // Play alert siren countdown

                }

            } else {

                // Boss handling

                if (sirenTimer > 0) {

                    sirenTimer -= dt;

                    // Play rapid siren beep

                    if (Math.floor(sirenTimer * 10) % 4 === 0) {

                        playSound('siren');

                    }

                    if (sirenTimer <= 0) {

                        boss = new Boss();

                    }

                } else if (boss) {

                    boss.update(dt);

                }

            }


            // Update Bullets

            for (let i = bullets.length - 1; i >= 0; i--) {

                const b = bullets[i];

                b.update(dt);

                if (b.x > canvas.width + 20) {

                    bullets.splice(i, 1);

                }

            }


            // Update Enemy Bullets

            for (let i = enemyBullets.length - 1; i >= 0; i--) {

                const eb = enemyBullets[i];

                eb.update(dt);

                

                // Collision with player

                const ebBox = { x: eb.x - eb.size, y: eb.y - eb.size, width: eb.size*2, height: eb.size*2 };

                if (checkCollision(ebBox, player)) {

                    player.takeDamage(12);

                    enemyBullets.splice(i, 1);

                    continue;

                }


                if (eb.x < -20) {

                    enemyBullets.splice(i, 1);

                }

            }


            // Update Enemies

            for (let i = enemies.length - 1; i >= 0; i--) {

                const e = enemies[i];

                e.update(dt);


                // Collision with player

                if (checkCollision(e, player)) {

                    player.takeDamage(20);

                    createExplosion(e.x + e.width/2, e.y + e.height/2, e.color, 10);

                    enemies.splice(i, 1);

                    continue;

                }


                // Collision with player bullets

                for (let j = bullets.length - 1; j >= 0; j--) {

                    const b = bullets[j];

                    const bBox = { x: b.x - b.size, y: b.y - 2, width: b.size*2, height: 4 };

                    if (checkCollision(bBox, e)) {

                        e.hp -= (player.weaponLevel >= 4 ? 2 : 1);

                        bullets.splice(j, 1);

                        playSound('hit');


                        if (e.hp <= 0) {

                            createExplosion(e.x + e.width/2, e.y + e.height/2, e.color, 12);

                            playSound('explosion');

                            score += e.scoreValue;


                            // Potential Power Up Drop (15% chance for weapon, 8% for shield)

                            const dropChance = Math.random();

                            if (dropChance < 0.15) {

                                powerups.push(new PowerUp(e.x, e.y, 'W'));

                            } else if (dropChance < 0.23) {

                                powerups.push(new PowerUp(e.x, e.y, 'S'));

                            }


                            enemies.splice(i, 1);

                            break;

                        }

                    }

                }


                // Remove off-screen enemies

                if (e.x < -60) {

                    enemies.splice(i, 1);

                }

            }


            // Update Boss collisions if active

            if (boss) {

                // Check player bullet hits on boss

                for (let j = bullets.length - 1; j >= 0; j--) {

                    const b = bullets[j];

                    const bBox = { x: b.x - b.size, y: b.y - 2, width: b.size*2, height: 4 };

                    if (checkCollision(bBox, boss)) {

                        const dmg = player.weaponLevel >= 4 ? 2 : 1;

                        boss.takeDamage(dmg);

                        bullets.splice(j, 1);

                    }

                }


                // Check boss body collision with player

                if (checkCollision(player, boss)) {

                    player.takeDamage(35);

                }


                // Big laser beam damage tracking

                if (boss.state === 'laser_fire') {

                    // Laser occupies vertical block from boss.y + 50 to boss.y + 90

                    const laserYStart = boss.y + 50;

                    const laserHeight = 40;

                    if (player.x + player.width > 0 && player.x < boss.x + 20) {

                        if (player.y + player.height > laserYStart && player.y < laserYStart + laserHeight) {

                            player.takeDamage(3); // Severe continuous laser damage

                        }

                    }

                }

            }


            // Update Powerups

            for (let i = powerups.length - 1; i >= 0; i--) {

                const pu = powerups[i];

                pu.update(dt);


                if (checkCollision(pu, player)) {

                    playSound('powerup');

                    if (pu.kind === 'W') {

                        player.weaponLevel = Math.min(5, player.weaponLevel + 1);

                    } else if (pu.kind === 'S') {

                        player.shield = Math.min(player.shieldMax, player.shield + 30);

                    }

                    powerups.splice(i, 1);

                    continue;

                }


                if (pu.x < -30) {

                    powerups.splice(i, 1);

                }

            }


            // Particles

            for (let i = particles.length - 1; i >= 0; i--) {

                const p = particles[i];

                p.update(dt);

                if (p.alpha <= 0) {

                    particles.splice(i, 1);

                }

            }


            // Sync HTML UI Overlays

            uiShield.innerText = Math.round(player.shield) + '%';

            uiShield.style.color = player.shield > 40 ? '#00ff00' : '#ff0033';

            uiWeapon.innerText = 'LVL ' + player.weaponLevel + (player.weaponLevel === 5 ? ' (MAX)' : '');

            uiScore.innerText = score;

        }


        // --- Draw Render Step ---

        function draw() {

            // Clear Frame

            ctx.fillStyle = '#010108';

            ctx.fillRect(0, 0, canvas.width, canvas.height);


            // Stars

            stars.forEach(star => star.draw());


            // Player Bullets

            bullets.forEach(b => b.draw());


            // Enemy Bullets

            enemyBullets.forEach(eb => eb.draw());


            // Powerups

            powerups.forEach(pu => pu.draw());


            // Enemies

            enemies.forEach(e => e.draw());


            // Boss

            if (boss) boss.draw();


            // Player Ship

            player.draw();


            // Explosions / Particle layers

            particles.forEach(p => p.draw());


            // Boss warning alarm

            if (sirenTimer > 0) {

                ctx.fillStyle = 'rgba(255, 0, 0, ' + (Math.sin(gameTime * 20) * 0.2 + 0.25) + ')';

                ctx.fillRect(0, 0, canvas.width, canvas.height);


                ctx.fillStyle = '#ff0033';

                ctx.font = 'bold 32px monospace';

                ctx.textAlign = 'center';

                ctx.fillText('WARNING: BOSS ENGAGING', canvas.width / 2, canvas.height / 2 - 20);

                ctx.font = '16px monospace';

                ctx.fillText('CRITICAL SIGNALS DETECTED AHEAD', canvas.width / 2, canvas.height / 2 + 15);

            }


            // Boss HP Bar Draw

            if (boss && boss.state !== 'intro') {

                const barWidth = 300;

                const barHeight = 12;

                const bx = canvas.width / 2 - barWidth / 2;

                const by = 20;


                ctx.fillStyle = '#111';

                ctx.fillRect(bx, by, barWidth, barHeight);


                const hpPercent = boss.hp / boss.hpMax;

                ctx.fillStyle = hpPercent > 0.4 ? '#ff3300' : '#ff00ff';

                ctx.fillRect(bx, by, barWidth * hpPercent, barHeight);


                ctx.strokeStyle = '#fff';

                ctx.lineWidth = 1;

                ctx.strokeRect(bx, by, barWidth, barHeight);


                ctx.fillStyle = '#fff';

                ctx.font = 'bold 11px monospace';

                ctx.textAlign = 'center';

                ctx.fillText('CYBER COELACANTH', canvas.width / 2, by - 6);

            }


            // Pause Overlay

            if (paused) {

                ctx.fillStyle = 'rgba(5, 5, 15, 0.75)';

                ctx.fillRect(0, 0, canvas.width, canvas.height);


                ctx.fillStyle = '#00ffff';

                ctx.font = 'bold 36px monospace';

                ctx.textAlign = 'center';

                ctx.fillText('SYSTEM PAUSED', canvas.width / 2, canvas.height / 2);

                ctx.font = '14px monospace';

                ctx.fillText('Press P to Resume System', canvas.width / 2, canvas.height / 2 + 30);

            }


            // Game Over Screen

            if (gameOver) {

                ctx.fillStyle = 'rgba(15, 5, 5, 0.85)';

                ctx.fillRect(0, 0, canvas.width, canvas.height);


                ctx.fillStyle = '#ff0033';

                ctx.font = 'bold 42px monospace';

                ctx.textAlign = 'center';

                ctx.fillText('FIGHTER CRUSHED', canvas.width / 2, canvas.height / 2 - 30);


                ctx.fillStyle = '#ffffff';

                ctx.font = '16px monospace';

                ctx.fillText('SCORE: ' + score, canvas.width / 2, canvas.height / 2 + 10);

                ctx.font = '14px monospace';

                ctx.fillStyle = '#8a8a9f';

                ctx.fillText('Click screen or press SPACE to retry', canvas.width / 2, canvas.height / 2 + 45);

            }


            // Game Won Screen

            if (gameWon) {

                ctx.fillStyle = 'rgba(5, 15, 10, 0.85)';

                ctx.fillRect(0, 0, canvas.width, canvas.height);


                ctx.fillStyle = '#00ff55';

                ctx.font = 'bold 42px monospace';

                ctx.textAlign = 'center';

                ctx.fillText('VICTORY ACHIEVED', canvas.width / 2, canvas.height / 2 - 40);


                ctx.fillStyle = '#ffffff';

                ctx.font = '18px monospace';

                ctx.fillText('SCORE: ' + score, canvas.width / 2, canvas.height / 2);

                ctx.fillStyle = '#00ffff';

                ctx.fillText('Cyber Coelacanth eradicated.', canvas.width / 2, canvas.height / 2 + 25);

                

                ctx.fillStyle = '#8a8a9f';

                ctx.font = '14px monospace';

                ctx.fillText('Click screen or press SPACE to replay', canvas.width / 2, canvas.height / 2 + 60);

            }

        }


        // --- Click triggers for restarts ---

        function handleInteraction() {

            if (gameOver || gameWon) {

                resetGame();

            }

        }

        canvas.addEventListener('click', handleInteraction);

        window.addEventListener('keydown', e => {

            if (e.key === ' ' && (gameOver || gameWon)) {

                resetGame();

            }

        });


        // Start Loop

        requestAnimationFrame(loop);

    </script>

</body>

</html>


```
