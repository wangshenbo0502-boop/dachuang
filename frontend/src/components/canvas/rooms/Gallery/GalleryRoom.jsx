import { useRef, useState, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useTexture, PositionalAudio } from '@react-three/drei';
import * as THREE from 'three';
import gsap from 'gsap';
import { Observer } from 'gsap/all';
import { useScene } from '../../../../context/SceneContext';
import { useJobMatch } from '../../../../context/JobMatchContext';
import { getJobDetail } from '../../../../api/jobMatch';
import { toJobDetailOverlay, toJobDetailErrorOverlay } from '../../../../adapters/jobMatch';
import { ApiError } from '../../../../api/index';

gsap.registerPlugin(Observer);
import { useAchievements } from '../../../../context/AchievementsContext';
import GalleryClouds from './GalleryClouds';
import { useAudio } from '../../../../context/AudioManager';
import { usePaintMaterial } from './usePaintMaterial';
import JobCard from './JobCard';
import { PROJECT_COUNT, GAP } from './galleryConstants';

export const AUDIO_SETTINGS = {
    volume: 0.6,
    distance: 2,
    rolloff: 1.5,
};

export const GALLERY_INTERACTION_AUDIO_SETTINGS = {
    volume: 0.6,
    distance: 2,
    rolloff: 2,
};

const BIRD_WIDTH = 0.49;
const BIRD_HEIGHT = 0.35;
const RIGHT_CROP_AMOUNT = 0.2;

const EMPTY_SLOT = {
    job_id: '',
    title: '',
    category: '',
    tags: [],
    snippet: '',
};

const GalleryRoom = ({ showRoom, onReady, isExiting, isWarmup }) => {
    const { openOverlay, isTeleporting } = useScene();
    const { displayItems, matchMap, mode } = useJobMatch();
    const { showTutorial, unlockAchievement, hidePopup } = useAchievements();
    const { globalVolume, isMuted } = useAudio();
    const effectiveVolume = isMuted ? 0 : AUDIO_SETTINGS.volume * globalVolume;

    const audioRef = useRef();
    useEffect(() => {
        if (audioRef.current?.setVolume) {
            audioRef.current.setVolume(effectiveVolume);
        }
    }, [effectiveVolume]);

    const groupRef = useRef();
    const targetScroll = useRef(0);
    const currentScroll = useRef(0);
    const [selectedCard, setSelectedCard] = useState(null);
    const [globalIsAnimating, setGlobalIsAnimating] = useState(false);
    const cardRefs = useRef([]);

    useEffect(() => {
        if (isExiting || isTeleporting) hidePopup();
    }, [isExiting, isTeleporting, hidePopup]);

    const { onBeforeCompile, animatePaint, resetPaint, uniformsData, updateRoomOrigin } = usePaintMaterial();
    const [isTransitioning, setIsTransitioning] = useState(false);
    const wasTeleportedRef = useRef(false);

    useEffect(() => {
        if (isTeleporting) wasTeleportedRef.current = true;
    }, [isTeleporting]);

    useEffect(() => {
        if (showRoom && !isWarmup) {
            if (wasTeleportedRef.current || isTeleporting) {
                uniformsData.uPaintProgress.value = 1.0;
                setIsTransitioning(false);
            } else {
                setIsTransitioning(true);
                resetPaint();
                animatePaint(0.2, 2.5);
                setTimeout(() => setIsTransitioning(false), 2700);
            }
        } else {
            uniformsData.uPaintProgress.value = 1.0;
        }
    }, [showRoom, isWarmup, isTeleporting]);

    useEffect(() => {
        setSelectedCard(null);
    }, [displayItems, mode]);

    const cards = useMemo(() => {
        return Array.from({ length: PROJECT_COUNT }, (_, i) => {
            if (displayItems.length === 0) {
                return { ...EMPTY_SLOT, job_id: `__slot_${i}`, hasData: false };
            }
            return { ...displayItems[i % displayItems.length], hasData: true };
        });
    }, [displayItems]);

    const handleViewDetail = async (job) => {
        if (!job?.job_id || job.job_id.startsWith('__')) return;
        try {
            const res = await getJobDetail(job.job_id);
            openOverlay(toJobDetailOverlay(res.data, matchMap[job.job_id] ?? null));
        } catch (err) {
            const msg = err instanceof ApiError ? err.message : err?.message || '加载详情失败';
            openOverlay(toJobDetailErrorOverlay(job, msg));
        }
    };

    const handleCardClick = async (clickedIndex) => {
        if (globalIsAnimating || isTransitioning || !cards[clickedIndex]?.hasData) return;
        unlockAchievement('gallery_inspect');
        if (selectedCard === clickedIndex) {
            setGlobalIsAnimating(true);
            await cardRefs.current[clickedIndex]?.closeCard();
            setSelectedCard(null);
            setGlobalIsAnimating(false);
        } else if (selectedCard !== null) {
            setGlobalIsAnimating(true);
            await cardRefs.current[selectedCard]?.closeCard();
            setSelectedCard(null);
            await cardRefs.current[clickedIndex]?.openCard();
            setSelectedCard(clickedIndex);
            setGlobalIsAnimating(false);
        } else {
            setGlobalIsAnimating(true);
            await cardRefs.current[clickedIndex]?.openCard();
            setSelectedCard(clickedIndex);
            setGlobalIsAnimating(false);
        }
    };

    const scrollToIndex = (index, onComplete) => {
        const totalWidth = PROJECT_COUNT * GAP;
        const targetScrollValue = index * GAP;
        const currentScrollValue = currentScroll.current;
        let diff = targetScrollValue - currentScrollValue;
        const halfWidth = totalWidth / 2;
        while (diff > halfWidth) diff -= totalWidth;
        while (diff < -halfWidth) diff += totalWidth;
        const finalTarget = currentScrollValue + diff;
        gsap.to(targetScroll, { current: finalTarget, duration: 0.5, ease: 'power2.inOut' });
        gsap.to(currentScroll, { current: finalTarget, duration: 0.5, ease: 'power2.inOut', onComplete });
    };

    const hasSignaledReady = useRef(false);
    const frameCount = useRef(0);

    useFrame(() => {
        updateRoomOrigin(groupRef);
        if (hasSignaledReady.current) return;
        frameCount.current++;
        if (frameCount.current >= 5) {
            hasSignaledReady.current = true;
            onReady?.();
            setTimeout(() => { if (!isWarmup) showTutorial('gallery_inspect'); }, 2000);
        }
    });

    const [canHover, setCanHover] = useState(() =>
        typeof window !== 'undefined' ? window.matchMedia('(hover: hover)').matches : true
    );

    useEffect(() => {
        const mq = window.matchMedia('(hover: hover)');
        const handleHoverChange = (e) => setCanHover(e.matches);
        mq.addEventListener('change', handleHoverChange);
        return () => mq.removeEventListener('change', handleHoverChange);
    }, []);

    const frontTextureRaw = useTexture(canHover ? '/textures/gallery/tylkartki_painted.webp' : '/textures/gallery/tylkartki.webp');
    const backTextureRaw = useTexture(canHover ? '/textures/gallery/tylkartki_painted.webp' : '/textures/gallery/tylkartki.webp');
    const buttonTextureRaw = useTexture(canHover ? '/textures/gallery/przyciskdotylukartki_painted.webp' : '/textures/gallery/przyciskdotylukartki.webp');
    const frontTexture = frontTextureRaw;
    const backTexture = backTextureRaw;
    const buttonTexture = buttonTextureRaw;
    const paintedTexture = canHover ? frontTextureRaw : null;

    [frontTextureRaw, backTextureRaw, buttonTextureRaw].forEach((t) => {
        if (t) t.colorSpace = THREE.SRGBColorSpace;
    });

    const floorTexture = useTexture('/textures/gallery/floor.webp');
    const railingTexture = useTexture('/textures/gallery/railing.webp');
    const housesTexture = useTexture('/textures/gallery/domki.webp');
    const cityTexture = useTexture('/textures/gallery/miastotlo.webp');
    const birdTexture = useTexture('/textures/gallery/bird_gray.webp');
    const clothespinTexture = useTexture('/textures/gallery/klamerka.webp');

    useEffect(() => {
        if (floorTexture) {
            floorTexture.wrapS = THREE.MirroredRepeatWrapping;
            floorTexture.wrapT = THREE.MirroredRepeatWrapping;
            floorTexture.repeat.set(0.5, 0.5 * 1.835);
            floorTexture.needsUpdate = true;
        }
        if (railingTexture) {
            railingTexture.wrapS = railingTexture.wrapT = THREE.RepeatWrapping;
            railingTexture.repeat.set(7, 1);
            railingTexture.needsUpdate = true;
        }
    }, [floorTexture, railingTexture]);

    const materials = useMemo(() => {
        const floorMat = new THREE.MeshBasicMaterial({ map: floorTexture, color: '#e0e0e0', side: THREE.DoubleSide });
        floorMat.onBeforeCompile = onBeforeCompile;
        floorMat.transparent = true;
        floorMat.needsUpdate = true;

        const ropeMat = new THREE.MeshBasicMaterial({ color: '#666666' });
        ropeMat.onBeforeCompile = onBeforeCompile;
        ropeMat.transparent = true;
        ropeMat.needsUpdate = true;

        const thresholdMat = new THREE.MeshBasicMaterial({
            color: '#e0e0e0',
            map: (() => {
                const t = new THREE.TextureLoader().load('/textures/corridor/texturadoprogow.webp');
                t.colorSpace = THREE.SRGBColorSpace;
                t.wrapS = t.wrapT = THREE.RepeatWrapping;
                t.repeat.set(15 / 2.524, 1);
                return t;
            })(),
            side: THREE.DoubleSide,
        });
        thresholdMat.onBeforeCompile = onBeforeCompile;
        thresholdMat.transparent = true;
        thresholdMat.needsUpdate = true;

        return { floor: floorMat, rope: ropeMat, threshold: thresholdMat };
    }, [floorTexture, onBeforeCompile]);

    const curve = useMemo(() => new THREE.CatmullRomCurve3([
        new THREE.Vector3(-16, 3.5, -6),
        new THREE.Vector3(-8, 2.5, -4.5),
        new THREE.Vector3(0, 1.8, -3),
        new THREE.Vector3(8, 2.5, -4.5),
        new THREE.Vector3(16, 3.5, -6),
    ]), []);

    const ropeGeometry = useMemo(() => new THREE.TubeGeometry(curve, 64, 0.015, 8, false), [curve]);

    const floorShape = useMemo(() => {
        const shape = new THREE.Shape();
        shape.moveTo(-1.1, -2.0);
        shape.lineTo(1.1, -2.0);
        shape.lineTo(7.5, 4);
        shape.lineTo(-7.5, 4);
        shape.lineTo(-1.1, -2.0);
        return shape;
    }, []);

    const lastTouchX = useRef(0);
    useEffect(() => {
        const scrollObserver = Observer.create({
            target: window,
            type: 'wheel,touch,pointer',
            wheelSpeed: -1,
            onWheel: (e) => {
                if (!showRoom || selectedCard !== null || globalIsAnimating || isTransitioning) return;
                e.event.preventDefault();
                targetScroll.current += e.event.deltaY * 0.005;
            },
            onPress: (e) => {
                if (!showRoom || selectedCard !== null || globalIsAnimating || isTransitioning) return;
                const orig = e.event;
                if (orig.touches?.length === 1) lastTouchX.current = orig.touches[0].clientX;
            },
            onDrag: (e) => {
                if (!showRoom || selectedCard !== null || globalIsAnimating || isTransitioning) return;
                const orig = e.event;
                if (orig.touches?.length === 1) {
                    const deltaX = lastTouchX.current - orig.touches[0].clientX;
                    lastTouchX.current = orig.touches[0].clientX;
                    targetScroll.current += deltaX * 0.008;
                }
            },
        });
        return () => scrollObserver.kill();
    }, [showRoom, selectedCard, globalIsAnimating, isTransitioning]);

    useFrame((_, delta) => {
        currentScroll.current = THREE.MathUtils.lerp(currentScroll.current, targetScroll.current, delta * 5);
    });

    const RAILING_HEIGHT = 1.25;

    return (
        <group ref={groupRef}>
            {!isWarmup && (
                <PositionalAudio
                    ref={audioRef}
                    url="/sounds/szummiasta.mp3"
                    distanceModel="exponential"
                    refDistance={AUDIO_SETTINGS.distance}
                    rolloffFactor={AUDIO_SETTINGS.rolloff}
                    loop
                    autoplay
                    volume={effectiveVolume}
                />
            )}
            <group position={[0, -0.7, -2]}>
                <mesh rotation={[-Math.PI / 2, 0, 0]}>
                    <shapeGeometry args={[floorShape]} />
                    <primitive object={materials.floor} />
                </mesh>

                <line rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
                    <bufferGeometry>
                        <float32BufferAttribute attach="attributes-position" count={2} array={new Float32Array([7.5, 4, 0, -7.5, 4, 0])} itemSize={3} />
                    </bufferGeometry>
                    <lineBasicMaterial color="#999999" onBeforeCompile={onBeforeCompile} transparent needsUpdate />
                </line>

                <mesh position={[0, RAILING_HEIGHT / 2, -3.9]}>
                    <planeGeometry args={[20, RAILING_HEIGHT]} />
                    <meshBasicMaterial color="#e0e0e0" map={railingTexture} transparent side={THREE.DoubleSide} alphaTest={0.1} onBeforeCompile={onBeforeCompile} customProgramCacheKey={() => 'railing-paint'} />
                </mesh>

                <mesh position={[0, 0.01, -3.9]} rotation={[-Math.PI / 2, 0, 0]}>
                    <planeGeometry args={[15, 0.15]} />
                    <primitive object={materials.threshold} />
                </mesh>

                <group position={[0, 1.6, -4]}>
                    <mesh geometry={ropeGeometry} material={materials.rope} />
                    {cards.map((job, i) => (
                        <JobCard
                            key={`card-${i}-${mode}-${job.job_id}`}
                            index={i}
                            ref={(el) => { cardRefs.current[i] = el; }}
                            job={job}
                            frontTexture={frontTexture}
                            paintedTexture={paintedTexture}
                            backTexture={backTexture}
                            buttonTexture={buttonTexture}
                            clothespinTexture={clothespinTexture}
                            currentScroll={currentScroll}
                            curve={curve}
                            isSelected={selectedCard === i}
                            scrollToIndex={scrollToIndex}
                            onClick={handleCardClick}
                            onViewDetail={handleViewDetail}
                            isMobile={!canHover}
                            isTransitioning={isTransitioning}
                            paintProgress={uniformsData.uPaintProgress}
                            roomOrigin={uniformsData.uRoomOrigin}
                            hasData={job.hasData}
                        />
                    ))}
                </group>

                <mesh position={[0, -1, -9]}>
                    <planeGeometry args={[15, 15 / 2.357]} />
                    <meshBasicMaterial color="#e0e0e0" map={housesTexture} transparent alphaTest={0.1} side={THREE.DoubleSide} onBeforeCompile={onBeforeCompile} />
                </mesh>
                <mesh position={[-15, -1, -9]} scale={[-1, 1, 1]}>
                    <planeGeometry args={[15, 15 / 2.357]} />
                    <meshBasicMaterial color="#e0e0e0" map={housesTexture} transparent alphaTest={0.1} side={THREE.DoubleSide} onBeforeCompile={onBeforeCompile} />
                </mesh>
                <RightSideHouses texture={housesTexture} baseWidth={15} baseHeight={15 / 2.357} cropAmount={RIGHT_CROP_AMOUNT} />

                <mesh position={[0, 3.4, -17]}>
                    <planeGeometry args={[30, 30 / 2.357]} />
                    <meshBasicMaterial color="#e0e0e0" map={cityTexture} transparent alphaTest={0.1} side={THREE.DoubleSide} onBeforeCompile={onBeforeCompile} />
                </mesh>
                <mesh position={[-30, 3.4, -17]} scale={[-1, 1, 1]}>
                    <planeGeometry args={[30, 30 / 2.357]} />
                    <meshBasicMaterial color="#e0e0e0" map={cityTexture} transparent alphaTest={0.1} side={THREE.DoubleSide} onBeforeCompile={onBeforeCompile} />
                </mesh>
                <mesh position={[30, 3.4, -17]} scale={[-1, 1, 1]}>
                    <planeGeometry args={[30, 30 / 2.357]} />
                    <meshBasicMaterial color="#e0e0e0" map={cityTexture} transparent alphaTest={0.1} side={THREE.DoubleSide} onBeforeCompile={onBeforeCompile} />
                </mesh>

                <FlyingBird texture={birdTexture} />
                <GalleryClouds count={65} seed={123} />

                <mesh position={[0, 5, -20]}>
                    <sphereGeometry args={[40, 32, 32]} />
                    <meshBasicMaterial color="#f0f0f0" side={THREE.BackSide} transparent opacity={0.5} onBeforeCompile={onBeforeCompile} />
                </mesh>
            </group>
        </group>
    );
};

const FlyingBird = ({ texture }) => {
    const birdRef = useRef();
    const velocityY = useRef(0);
    const jumpInterval = useRef(0);

    useFrame((_, delta) => {
        if (!birdRef.current) return;
        const safeDelta = Math.min(delta, 0.05);
        birdRef.current.position.x += 2.5 * safeDelta;
        if (birdRef.current.position.x > 25) {
            birdRef.current.position.x = -25;
            birdRef.current.position.y = 4.5;
            velocityY.current = 0;
            jumpInterval.current = 0;
            birdRef.current.rotation.z = 0;
        }
        velocityY.current += -12.0 * safeDelta;
        birdRef.current.position.y += velocityY.current * safeDelta;
        jumpInterval.current -= safeDelta;
        if (jumpInterval.current <= 0 || birdRef.current.position.y < 3.2) {
            velocityY.current = 5.5;
            jumpInterval.current = 0.9 + Math.random() * 0.3;
        }
        if (birdRef.current.position.y < 3.0) {
            birdRef.current.position.y = 3.0;
            velocityY.current = 5.5;
        }
        if (birdRef.current.position.y > 6.5) {
            birdRef.current.position.y = 6.5;
            velocityY.current = 0;
        }
        const targetRotationZ = THREE.MathUtils.clamp(velocityY.current * 0.05, -Math.PI / 6, Math.PI / 8);
        birdRef.current.rotation.z = THREE.MathUtils.lerp(birdRef.current.rotation.z, targetRotationZ, safeDelta * 8);
    });

    return (
        <mesh ref={birdRef} position={[-25, 4.5, -10]} scale={[BIRD_WIDTH, BIRD_HEIGHT, 1]}>
            <planeGeometry args={[1.5, 1.5]} />
            <meshBasicMaterial color="#e0e0e0" map={texture} transparent alphaTest={0.1} side={THREE.DoubleSide} />
        </mesh>
    );
};

const RightSideHouses = ({ texture, baseWidth, baseHeight, cropAmount }) => {
    const croppedTexture = useMemo(() => {
        const t = texture.clone();
        t.offset.x = cropAmount;
        t.repeat.x = 1 - cropAmount;
        t.needsUpdate = true;
        return t;
    }, [texture, cropAmount]);

    const newWidth = baseWidth * (1 - cropAmount);
    const newX = 7.5 + newWidth / 2;

    return (
        <mesh position={[newX, -1, -9]} scale={[-1, 1, 1]}>
            <planeGeometry args={[newWidth, baseHeight]} />
            <meshBasicMaterial color="#e0e0e0" map={croppedTexture} transparent alphaTest={0.1} side={THREE.DoubleSide} />
        </mesh>
    );
};

export default GalleryRoom;
