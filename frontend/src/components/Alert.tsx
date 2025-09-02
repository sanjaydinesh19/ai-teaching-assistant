import React from "react";

type Kind = "info" | "success" | "error";

export default function Alert({
  kind = "info",
  children,
}: {
  kind?: Kind;
  children: React.ReactNode;
}) {
  const styles =
    kind === "error"
      ? "bg-red-50 text-red-700 border-red-200"
      : kind === "success"
      ? "bg-green-50 text-green-700 border-green-200"
      : "bg-blue-50 text-blue-700 border-blue-200";
  return <div className={`border rounded-lg px-3 py-2 ${styles}`}>{children}</div>;
}
