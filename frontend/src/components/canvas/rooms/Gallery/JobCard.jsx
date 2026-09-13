/**
 * 文件名称：JobCard.jsx
 * 文件作用：岗位匹配 3D 纸张卡片 —— 动画骨架与参考版 ProjectCard 一致，仅替换岗位业务字段。
 */

import { useRef, useState, useEffect, forwardRef, useImperativeHandle, memo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, PositionalAudio } from '@react-three/drei';
import * as THREE from 'three';
import gsap from 'gsap';
import PaperMaterial from './PaperMaterial';
import { useAudio } from '../../../../context/AudioManager';
import { PROJECT_COUNT, GAP } from './galleryConstants';

const _tempScale = new THREE.Vector3();

const GALLERY_INTERACTION_AUDIO_SETTINGS = {
    volume: 0.6,
    distance: 2,
    rolloff: 2,
};

const JobCard = memo(forwardRef(({
    index,
    job,
    frontTexture,
    paintedTexture,
    backTexture,
    buttonTexture,
    clothespinTexture,
    currentScroll,
    curve,
    isSelected,
    scrollToIndex,
    onClick,
    onViewDetail,
    isMobile,
    isTransitioning,
    paintProgress,
    roomOrigin,
    hasData,
}, ref) => {
    const cardRef = useRef();
    const paperRef = useRef();
    const materialRef = useRef();
    const textRef = useRef();
    const buttonGroupRef = useRef();
    const detailsGroupRef = useRef();
    const tagsGroupRef = useRef();
    const detailsTextRef1 = useRef();
    const detailsTextRef2 = useRef();
    const tagsTextRef = useRef();
    const tagsLineRef = useRef();
    const scoreTextRef = useRef();
    const openTextRef = useRef();
    const [hovered, setHovered] = useState(false);
    const [btnHovered, setBtnHovered] = useState(false);
    const [isAnimating, setIsAnimating] = useState(false);
    const [isScrolling, setIsScrolling] = useState(false);
    const [detailLoading, setDetailLoading] = useState(false);

    const swaySpeed = useRef(Math.random() * 0.2 + 0.3);
    const swayOffset = useRef(Math.random() * 100);
    const paperAudioRef = useRef();
    const { globalVolume, isMuted } = useAudio();

    const playPaperSound = () => {
        if (paperAudioRef.current) {
            const vol = isMuted ? 0 : GALLERY_INTERACTION_AUDIO_SETTINGS.volume * globalVolume;
            paperAudioRef.current.setVolume(vol);
            if (paperAudioRef.current.isPlaying) paperAudioRef.current.stop();
            paperAudioRef.current.play();
        }
    };

    useImperativeHandle(ref, () => ({
        closeCard: () => {
            return new Promise((resolve) => {
                setIsAnimating(true);
                playPaperSound();

                const timeline = gsap.timeline({
                    onComplete: () => {
                        setIsAnimating(false);
                        resolve();
                        if (paintedTexture && materialRef.current) {
                            gsap.to(materialRef.current, {
                                uProgress: 0.0,
                                duration: 0.5,
                                ease: 'power2.out',
                                overwrite: 'auto',
                            });
                        }
                    },
                });

                const localBaseY = -1.1;

                timeline.to(paperRef.current.position, {
                    y: localBaseY + 0.6,
                    x: 0,
                    z: 1,
                    duration: 0.35,
                    ease: 'power2.in',
                });

                timeline.to(paperRef.current.rotation, {
                    x: 0.5,
                    z: -0.05,
                    y: 0,
                    duration: 0.35,
                    ease: 'power2.in',
                }, '<');

                if (materialRef.current) {
                    timeline.to(materialRef.current, {
                        bend: 0.6,
                        duration: 0.3,
                        ease: 'power2.in',
                    }, '<');
                }

                timeline.to(paperRef.current.scale, {
                    x: 1, y: 1, z: 1,
                    duration: 0.3, ease: 'sine.inOut',
                }, '<');

                timeline.to(paperRef.current.position, {
                    y: localBaseY,
                    x: 0,
                    z: 0,
                    duration: 0.25,
                    ease: 'power3.out',
                });

                timeline.to(paperRef.current.rotation, {
                    x: 0, y: 0, z: 0,
                    duration: 0.25,
                    ease: 'power3.out',
                }, '<');

                if (materialRef.current) {
                    timeline.to(materialRef.current, {
                        bend: 0,
                        duration: 0.3,
                        ease: 'power2.out',
                    }, '<');
                }
            });
        },
        openCard: () => {
            return new Promise((resolve) => {
                setIsScrolling(true);
                scrollToIndex(index, () => {
                    setIsScrolling(false);
                    setIsAnimating(true);
                    playPaperSound();

                    const isMobileView = window.innerWidth < 768;
                    const targetX_World = 0;
                    const targetY_World = isMobileView ? -0.2 : 0.1;
                    const targetZ_World = isMobileView ? 0.5 : 1.5;

                    const parentPos = cardRef.current.position;
                    const targetX = targetX_World - parentPos.x;
                    const targetY = targetY_World - parentPos.y;
                    const targetZ = targetZ_World - parentPos.z;

                    const timeline = gsap.timeline({
                        onComplete: () => {
                            setIsAnimating(false);
                            resolve();
                        },
                    });

                    timeline.to(cardRef.current.rotation, {
                        x: 0, y: 0, z: 0,
                        duration: 0.3,
                        ease: 'power2.out',
                    }, 0);

                    if (materialRef.current) materialRef.current.bend = 0;

                    const localBaseY = -1.1;

                    timeline.to(paperRef.current.position, {
                        y: localBaseY - 0.5,
                        duration: 0.15,
                        ease: 'power2.out',
                    });

                    timeline.to(paperRef.current.rotation, {
                        x: 0.5,
                        z: -0.05,
                        duration: 0.15,
                        ease: 'power2.out',
                    }, '<');

                    if (materialRef.current) {
                        timeline.to(materialRef.current, {
                            bend: 0.8,
                            duration: 0.15,
                            ease: 'power2.out',
                        }, '<');

                        if (paintedTexture) {
                            gsap.to(materialRef.current, {
                                uProgress: 1.0,
                                duration: 0.3,
                                ease: 'power2.out',
                                overwrite: 'auto',
                            });
                        }
                    }

                    timeline.to(paperRef.current.position, {
                        y: localBaseY + 1.5,
                        x: targetX * 0.2,
                        z: targetZ * 0.2,
                        duration: 0.4,
                        ease: 'power1.out',
                    });

                    timeline.to(paperRef.current.rotation, {
                        x: Math.PI * 0.8,
                        z: 0.05,
                        y: -0.02,
                        duration: 0.4,
                        ease: 'power1.inOut',
                    }, '<');

                    if (materialRef.current) {
                        timeline.to(materialRef.current, {
                            bend: -0.3,
                            duration: 0.4,
                            ease: 'power1.inOut',
                        }, '<');
                    }

                    timeline.to(paperRef.current.position, {
                        y: targetY,
                        x: targetX,
                        z: targetZ,
                        duration: 0.4,
                        ease: 'power3.out',
                    });

                    timeline.to(paperRef.current.rotation, {
                        x: Math.PI,
                        y: 0,
                        z: 0,
                        duration: 0.4,
                        ease: 'power3.out',
                    }, '<');

                    if (materialRef.current) {
                        timeline.to(materialRef.current, {
                            bend: 0,
                            duration: 0.5,
                            ease: 'power2.out',
                        }, '<');
                    }

                    timeline.to(paperRef.current.scale, {
                        x: 1.1,
                        y: 1.1,
                        z: 1.1,
                        duration: 0.3,
                        ease: 'sine.out',
                    }, '-=0.4');
                });
            });
        },
    }));

    const handleClick = (e) => {
        e.stopPropagation();
        if (!hasData) return;
        if (onClick) onClick(index);
    };

    const handleViewDetail = async (e) => {
        e.stopPropagation();
        if (!isSelected || isTransitioning || !hasData || detailLoading) return;
        setDetailLoading(true);
        try {
            await onViewDetail?.(job);
        } finally {
            setDetailLoading(false);
        }
    };

    useEffect(() => {
        if (btnHovered && isSelected) {
            document.body.style.cursor = 'pointer';
        } else if (hovered && !isSelected && hasData) {
            document.body.style.cursor = 'pointer';
        } else {
            document.body.style.cursor = 'auto';
        }
        return () => { document.body.style.cursor = 'auto'; };
    }, [hovered, isSelected, btnHovered, hasData]);

    const snippet = hasData ? (job?.snippet || '').slice(0, 160) : '';
    const tagsLine = hasData ? (job?.tags ?? []).slice(0, 5).join(' · ') : '';
    const scoreLine = hasData && job?.match_score != null ? `匹配度 ${Math.round(job.match_score)}%` : '';
    const title = hasData ? (job?.title || '岗位') : '';

    useFrame((state) => {
        if (!cardRef.current) return;

        if (textRef.current && paintProgress) {
            const p = paintProgress.value;
            const expectedOpacity = p >= 1.0 ? 1.0 : THREE.MathUtils.clamp((p - 0.3) * 2.0, 0.0, 1.0);

            if (textRef.current.fillOpacity !== expectedOpacity) {
                const applyOpacity = (r) => {
                    if (r.current) {
                        r.current.fillOpacity = expectedOpacity;
                        if (r.current.material) {
                            r.current.material.opacity = expectedOpacity;
                            r.current.material.transparent = true;
                        }
                    }
                };
                applyOpacity(textRef);
                applyOpacity(detailsTextRef1);
                applyOpacity(detailsTextRef2);
                applyOpacity(tagsTextRef);
                applyOpacity(tagsLineRef);
                applyOpacity(scoreTextRef);
                applyOpacity(openTextRef);
            }
        }

        if (textRef.current && materialRef.current) {
            const y = textRef.current.position.y;
            const uBend = materialRef.current.bend;
            const uWindStrength = materialRef.current.windStrength || 0;
            const uTime = state.clock.getElapsedTime();
            const bendAmount = Math.pow(y, 2.0) * uBend;
            const totalWind = 0.02 + uWindStrength;
            const flutter = Math.sin(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            textRef.current.position.z = bendAmount + flutter + 0.02;
            const dz_dy = 2.0 * y * uBend + 2.0 * Math.cos(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            textRef.current.rotation.x = Math.atan(dz_dy);
        }

        if (buttonGroupRef.current && materialRef.current) {
            const y = buttonGroupRef.current.position.y;
            const uBend = materialRef.current.bend;
            const uWindStrength = materialRef.current.windStrength || 0;
            const uTime = state.clock.getElapsedTime();
            const bendAmount = Math.pow(y, 2.0) * uBend;
            const totalWind = 0.02 + uWindStrength;
            const flutter = Math.sin(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            buttonGroupRef.current.position.z = bendAmount + flutter - 0.03;
            const dz_dy = 2.0 * y * uBend + 2.0 * Math.cos(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            buttonGroupRef.current.rotation.x = Math.PI + Math.atan(dz_dy);
            const targetScale = btnHovered ? 1.08 : 1;
            buttonGroupRef.current.scale.lerp(_tempScale.set(targetScale, targetScale, 1), 0.15);
        }

        if (detailsGroupRef.current && materialRef.current) {
            const y = detailsGroupRef.current.position.y;
            const uBend = materialRef.current.bend;
            const uWindStrength = materialRef.current.windStrength || 0;
            const uTime = state.clock.getElapsedTime();
            const bendAmount = Math.pow(y, 2.0) * uBend;
            const totalWind = 0.02 + uWindStrength;
            const flutter = Math.sin(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            detailsGroupRef.current.position.z = bendAmount + flutter - 0.03;
            const dz_dy = 2.0 * y * uBend + 2.0 * Math.cos(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            detailsGroupRef.current.rotation.x = Math.PI + Math.atan(dz_dy);
        }

        if (tagsGroupRef.current && materialRef.current) {
            const y = tagsGroupRef.current.position.y;
            const uBend = materialRef.current.bend;
            const uWindStrength = materialRef.current.windStrength || 0;
            const uTime = state.clock.getElapsedTime();
            const bendAmount = Math.pow(y, 2.0) * uBend;
            const totalWind = 0.02 + uWindStrength;
            const flutter = Math.sin(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            tagsGroupRef.current.position.z = bendAmount + flutter - 0.03;
            const dz_dy = 2.0 * y * uBend + 2.0 * Math.cos(uTime * 2.0 + y * 2.0) * totalWind * (1.0 + Math.abs(uBend * 3.0));
            tagsGroupRef.current.rotation.x = Math.PI + Math.atan(dz_dy);
        }

        if (isAnimating || isSelected) return;

        const totalWidth = PROJECT_COUNT * GAP;
        let rawX = (index * GAP) - currentScroll.current;
        const halfWidth = totalWidth / 2;
        let displayX = ((rawX + halfWidth) % totalWidth + totalWidth) % totalWidth - halfWidth;

        const u = (displayX + 16) / 32;
        const safeU = THREE.MathUtils.clamp(u, 0, 1);
        const pointOnCurve = curve.getPointAt(safeU);

        cardRef.current.position.set(pointOnCurve.x, pointOnCurve.y, pointOnCurve.z);

        const time = state.clock.getElapsedTime();
        const wind = Math.sin(time * swaySpeed.current + swayOffset.current) * 0.05;
        cardRef.current.rotation.z = wind;
        cardRef.current.rotation.x = 0;

        const dist = Math.abs(displayX);
        const scale = THREE.MathUtils.clamp(1 - (dist / 50), 0.7, 1);
        cardRef.current.scale.setScalar(scale);
    });

    return (
        <group
            ref={cardRef}
            onClick={handleClick}
            onPointerEnter={(e) => {
                if (isMobile || isTransitioning || !hasData) return;
                e.stopPropagation();
                setHovered(true);
                if (materialRef.current && paintedTexture && !isSelected) {
                    gsap.to(materialRef.current, {
                        uProgress: 1.0,
                        duration: 0.8,
                        ease: 'power2.out',
                        overwrite: 'auto',
                    });
                }
            }}
            onPointerLeave={(e) => {
                if (isMobile || isTransitioning || !hasData) return;
                e.stopPropagation();
                setHovered(false);
                if (materialRef.current && paintedTexture && !isSelected) {
                    gsap.to(materialRef.current, {
                        uProgress: 0.0,
                        duration: 0.5,
                        ease: 'power2.out',
                        overwrite: 'auto',
                    });
                }
            }}
        >
            <mesh position={[0, -0.08, 0.15]} rotation={[0, 0, Math.PI]}>
                <planeGeometry args={[0.3, 0.2]} />
                <meshBasicMaterial
                    color="#ffffff"
                    map={clothespinTexture}
                    transparent
                    alphaTest={0.1}
                    side={THREE.DoubleSide}
                />
            </mesh>

            <group ref={paperRef} position={[0, -1.1, 0]}>
                <mesh>
                    <planeGeometry args={[1.5, 2, 16, 16]} />
                    <PaperMaterial
                        ref={materialRef}
                        color="#ffffff"
                        map={frontTexture}
                        mapBack={backTexture}
                        mapPainted={paintedTexture}
                        side={THREE.DoubleSide}
                        roughness={0.6}
                        paintProgress={paintProgress}
                        roomOrigin={roomOrigin}
                    />
                </mesh>

                <group ref={buttonGroupRef} position={[0, 0.75, 0]} rotation={[Math.PI, 0, 0]}>
                    <mesh>
                        <planeGeometry args={[1.2, 1.2 / 3.613]} />
                        <meshBasicMaterial color="#ffffff" map={buttonTexture} transparent alphaTest={0.05} />
                    </mesh>
                    <Text
                        ref={openTextRef}
                        position={[0, 0, 0.01]}
                        fontSize={0.11}
                        color={btnHovered ? '#333333' : '#1c1c1c'}
                        font="/fonts/CabinSketch-Bold.ttf"
                        anchorX="center"
                        anchorY="middle"
                        fillOpacity={0}
                    >
                        {detailLoading ? '加载中…' : '查看详情'}
                    </Text>
                    <mesh
                        position={[0, 0, 0.02]}
                        onClick={handleViewDetail}
                        onPointerEnter={(e) => {
                            if (isSelected && !isTransitioning && hasData) {
                                e.stopPropagation();
                                setBtnHovered(true);
                            }
                        }}
                        onPointerLeave={(e) => {
                            if (isSelected && !isTransitioning) e.stopPropagation();
                            setBtnHovered(false);
                        }}
                    >
                        <planeGeometry args={[1.2, 1.2 / 3.613]} />
                        <meshBasicMaterial color="#e0e0e0" transparent opacity={0} />
                    </mesh>
                </group>

                <group ref={detailsGroupRef} position={[0, -0.5, 0]} rotation={[Math.PI, 0, 0]}>
                    <Text
                        ref={detailsTextRef1}
                        position={[0, 0.28, 0.01]}
                        fontSize={0.10}
                        color="#1c1c1c"
                        font="/fonts/CabinSketch-Bold.ttf"
                        anchorX="center"
                        anchorY="middle"
                        fillOpacity={0}
                    >
                        岗位摘要
                    </Text>
                    <Text
                        ref={detailsTextRef2}
                        position={[0, 0.2, 0.01]}
                        fontSize={0.06}
                        color="#333333"
                        font="/fonts/CabinSketch-Bold.ttf"
                        anchorX="center"
                        anchorY="top"
                        maxWidth={1.1}
                        lineHeight={1.4}
                        textAlign="center"
                        fillOpacity={0}
                    >
                        {snippet || (hasData ? '展开后点击「查看详情」' : '')}
                    </Text>
                    {scoreLine ? (
                        <Text
                            ref={scoreTextRef}
                            position={[0, -0.02, 0.01]}
                            fontSize={0.07}
                            color="#1a1a1a"
                            font="/fonts/CabinSketch-Bold.ttf"
                            anchorX="center"
                            anchorY="middle"
                            fillOpacity={0}
                        >
                            {scoreLine}
                        </Text>
                    ) : null}
                </group>

                <group ref={tagsGroupRef} position={[0, 0.30, 0]} rotation={[Math.PI, 0, 0]}>
                    <Text
                        ref={tagsTextRef}
                        position={[0, 0.15, 0.01]}
                        fontSize={0.08}
                        color="#1c1c1c"
                        font="/fonts/CabinSketch-Bold.ttf"
                        anchorX="center"
                        anchorY="middle"
                        fillOpacity={0}
                    >
                        技能标签
                    </Text>
                    <Text
                        ref={tagsLineRef}
                        position={[0, -0.05, 0.01]}
                        fontSize={0.055}
                        color="#555555"
                        font="/fonts/CabinSketch-Bold.ttf"
                        anchorX="center"
                        anchorY="middle"
                        maxWidth={1.1}
                        textAlign="center"
                        fillOpacity={0}
                    >
                        {tagsLine}
                    </Text>
                </group>

                <Text
                    ref={textRef}
                    position={[0, 0.7, 0]}
                    fontSize={0.20}
                    color="#1c1c1c"
                    font="/fonts/CabinSketch-Bold.ttf"
                    anchorX="center"
                    anchorY="middle"
                    maxWidth={1.2}
                    textAlign="center"
                    fillOpacity={0}
                >
                    {title}
                </Text>

                <PositionalAudio
                    ref={paperAudioRef}
                    url="/sounds/papersound.mp3"
                    distanceModel="exponential"
                    rolloffFactor={GALLERY_INTERACTION_AUDIO_SETTINGS.rolloff}
                    refDistance={GALLERY_INTERACTION_AUDIO_SETTINGS.distance}
                    loop={false}
                />
            </group>
        </group>
    );
}));

export default JobCard;
