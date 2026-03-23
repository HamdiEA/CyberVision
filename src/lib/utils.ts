// Utilitaires frontend partages.
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Fusionne proprement les classes CSS conditionnelles.
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}