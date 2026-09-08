import { useScene } from '../../context/SceneContext';
import { useGalleryProjects, useStudioContent, useAwards } from '../../hooks/useSanityData';
import '../../styles/ScreenReaderOverlay.scss';

/**
 * ScreenReaderOverlay — 无障碍朗读层
 * 为 3D 画布内容提供屏幕阅读器可访问的 HTML 导航。
 */
const ScreenReaderOverlay = () => {
    const { hasEntered, isInRoom, currentRoom, teleportTo, requestExit } = useScene();

    const projects = useGalleryProjects();
    const studio = useStudioContent();
    const awards = useAwards();

    const roomNames = {
        about: '就业画像',
        gallery: '岗位匹配',
        contact: '联系反馈',
        studio: 'AI 工作台',
    };

    return (
        <div className="sr-overlay" role="complementary" aria-label="3D 应用无障碍导航">
            <a href="#sr-main-nav" className="sr-only sr-focusable">
                跳转到无障碍导航
            </a>

            <nav id="sr-main-nav" className="sr-only" aria-label="功能房间导航">
                <h1>AI就业竞争力分析助手</h1>
                <h2>功能导航</h2>

                {!hasEntered && (
                    <p>欢迎体验 AI 就业竞争力分析助手的 3D 交互界面。点击或按 Enter 进入大门。</p>
                )}

                {hasEntered && !isInRoom && (
                    <>
                        <p>你正在走廊中，选择一个功能房间：</p>
                        <ul>
                            <li>
                                <button onClick={() => teleportTo('about')} type="button">
                                    就业画像 — 个人资料与 AI 能力评估
                                </button>
                            </li>
                            <li>
                                <button onClick={() => teleportTo('gallery')} type="button">
                                    岗位匹配 — 搜索岗位与技能比对
                                </button>
                            </li>
                            <li>
                                <button onClick={() => teleportTo('contact')} type="button">
                                    联系反馈 — 提交建议与问题
                                </button>
                            </li>
                            <li>
                                <button onClick={() => teleportTo('studio')} type="button">
                                    AI 工作台 — 简历优化与成长规划
                                </button>
                            </li>
                        </ul>
                    </>
                )}

                {hasEntered && isInRoom && (
                    <>
                        <p>你已进入「{roomNames[currentRoom] || currentRoom}」房间。</p>
                        <button onClick={requestExit} type="button">
                            返回走廊
                        </button>

                        {currentRoom === 'about' && (
                            <div aria-label="就业画像内容">
                                <h3>就业画像</h3>
                                <p>维护个人资料、竞赛经历与技能，生成 AI 就业竞争力画像。</p>
                                {awards && (
                                    <section>
                                        <h4>竞赛与荣誉</h4>
                                        <ul>
                                            {awards.sotd?.items?.map((a, i) => (
                                                <li key={`sotd-${i}`}>{a.label} — {a.date}</li>
                                            ))}
                                            {awards.sotm?.items?.map((a, i) => (
                                                <li key={`sotm-${i}`}>{a.label} — {a.date}</li>
                                            ))}
                                            {awards.other?.items?.map((a, i) => (
                                                <li key={`other-${i}`}>{a.label} — {a.date}</li>
                                            ))}
                                        </ul>
                                    </section>
                                )}
                            </div>
                        )}
                        {currentRoom === 'gallery' && (
                            <div aria-label="岗位匹配内容">
                                <h3>岗位匹配</h3>
                                <p>浏览岗位卡片，点击查看详情与匹配结果。</p>
                                {projects?.length > 0 && (
                                    <ul>
                                        {projects.map((p, i) => (
                                            <li key={i}>
                                                <h4>{p.title}</h4>
                                                <p>{p.description}</p>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        )}
                        {currentRoom === 'contact' && (
                            <div aria-label="联系反馈内容">
                                <h3>联系反馈</h3>
                                <p>填写反馈表单，或查看联系方式。</p>
                            </div>
                        )}
                        {currentRoom === 'studio' && (
                            <div aria-label="AI 工作台内容">
                                <h3>AI 工作台</h3>
                                <p>浏览 AI 简历优化与成长规划的历史记录。</p>
                                {studio?.length > 0 && (
                                    <ul>
                                        {studio.map((s, i) => (
                                            <li key={i}>
                                                <h4>{s.title}（{s.platform}）</h4>
                                                <p>{s.description}</p>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        )}

                        <h3>快速导航</h3>
                        <ul>
                            {currentRoom !== 'about' && (
                                <li><button onClick={() => teleportTo('about')} type="button">前往就业画像</button></li>
                            )}
                            {currentRoom !== 'gallery' && (
                                <li><button onClick={() => teleportTo('gallery')} type="button">前往岗位匹配</button></li>
                            )}
                            {currentRoom !== 'contact' && (
                                <li><button onClick={() => teleportTo('contact')} type="button">前往联系反馈</button></li>
                            )}
                            {currentRoom !== 'studio' && (
                                <li><button onClick={() => teleportTo('studio')} type="button">前往 AI 工作台</button></li>
                            )}
                        </ul>
                    </>
                )}
            </nav>

            <div aria-live="polite" aria-atomic="true" className="sr-only">
                {isInRoom && `已进入${roomNames[currentRoom] || currentRoom}房间`}
            </div>
        </div>
    );
};

export default ScreenReaderOverlay;
