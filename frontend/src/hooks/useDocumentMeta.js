import { useEffect, useRef } from 'react';
import { useScene } from '../context/SceneContext';

/**
 * useDocumentMeta — 动态 Meta 标签与虚拟路由（History API）
 */

const ROOM_META = {
    null: {
        path: '/',
        title: 'AI就业竞争力分析助手 — 3D 沉浸式体验',
        description: '面向计算机专业大学生的 AI 就业竞争力分析平台。在手绘风 3D 走廊中探索就业画像、岗位匹配、简历优化与成长规划。',
    },
    about: {
        path: '/about',
        title: '就业画像 — AI就业竞争力分析助手',
        description: '维护个人资料与学习经历，生成 AI 就业画像、技术能力评估与竞争力评分。',
    },
    gallery: {
        path: '/gallery',
        title: '岗位匹配 — AI就业竞争力分析助手',
        description: '搜索岗位知识库，用技能与岗位需求智能比对，输出匹配度与差距清单。',
    },
    studio: {
        path: '/studio',
        title: 'AI 工作台 — AI就业竞争力分析助手',
        description: '简历优化与成长规划 — 在 3D 显示器塔中浏览 AI 分析历史与生成结果。',
    },
    contact: {
        path: '/contact',
        title: '联系反馈 — AI就业竞争力分析助手',
        description: '提交反馈与建议，获取平台使用帮助。',
    },
};

const PATH_TO_ROOM = {
    '/': null,
    '/about': 'about',
    '/gallery': 'gallery',
    '/studio': 'studio',
    '/contact': 'contact',
};

export function getInitialRoomFromUrl() {
    const path = window.location.pathname.replace(/\/+$/, '') || '/';
    return PATH_TO_ROOM[path] !== undefined ? PATH_TO_ROOM[path] : null;
}

export function useDocumentMeta() {
    const { currentRoom, teleportTo, hasEntered } = useScene();
    const isHandlingPopState = useRef(false);
    const lastPushedRoom = useRef(undefined);

    useEffect(() => {
        const roomKey = currentRoom === null ? 'null' : currentRoom;
        const meta = ROOM_META[roomKey] || ROOM_META['null'];

        document.title = meta.title;

        const descTag = document.querySelector('meta[name="description"]');
        if (descTag) {
            descTag.setAttribute('content', meta.description);
        }

        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) ogTitle.setAttribute('content', meta.title);

        const ogDesc = document.querySelector('meta[property="og:description"]');
        if (ogDesc) ogDesc.setAttribute('content', meta.description);

        if (!isHandlingPopState.current && lastPushedRoom.current !== currentRoom) {
            if (lastPushedRoom.current === undefined) {
                window.history.replaceState({ room: currentRoom }, '', meta.path);
            } else {
                window.history.pushState({ room: currentRoom }, '', meta.path);
            }
            lastPushedRoom.current = currentRoom;
        }

        isHandlingPopState.current = false;
    }, [currentRoom]);

    useEffect(() => {
        const handlePopState = (event) => {
            isHandlingPopState.current = true;
            const targetRoom = event.state?.room ?? null;
            lastPushedRoom.current = targetRoom;

            if (targetRoom === null) {
                const meta = ROOM_META['null'];
                document.title = meta.title;
            } else if (hasEntered) {
                teleportTo(targetRoom);
            }
        };

        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, [teleportTo, hasEntered]);
}
