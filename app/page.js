import SimulationButton from "./components/buttons/simulation-button";
import LowerHalfPage from "./components/main-lower-half/page";
import styles from "./page.module.css";

export default function HomePage() {
  return (
    <main className={`${styles.page} flex min-h-screen items-center justify-center overflow-hidden px-6`}>
      <div aria-hidden="true" className={styles.glow} />
      <div aria-hidden="true" className={styles.frame} />
      <div className="relative z-10 flex flex-col items-center gap-8 text-center">
        <h1
          className={`${styles.title} text-[clamp(3.5rem,10vw,7rem)] font-semibold uppercase leading-[0.92] tracking-[0.16em] text-stone-50 drop-shadow-[0_18px_40px_rgba(6,17,16,0.35)]`}
        >
          Tennis Predictor
        </h1>
        <LowerHalfPage />
      </div>
    </main>
  );
}
