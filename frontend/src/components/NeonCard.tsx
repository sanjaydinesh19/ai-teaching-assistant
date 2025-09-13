import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ReactNode } from "react";

type Props = {
  to: string;
  icon: ReactNode;
  title: string;
  desc: string;
};

export default function NeonCard({ to, icon, title, desc }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -4, scale: 1.01 }}
      className="rounded-2xl p-5 glass neon-glow"
    >
      <Link to={to} className="block">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-xl bg-white/5 border border-white/10">
            {icon}
          </div>
          <h3 className="font-display text-lg">{title}</h3>
        </div>
        <p className="text-white/70 text-sm leading-relaxed">{desc}</p>
        <div className="mt-4 text-neon.blue text-sm">Open →</div>
      </Link>
    </motion.div>
  );
}
