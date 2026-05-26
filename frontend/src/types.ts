export type Role = "user" | "assistant" | "error" | "system";

export type Message = {
  id: string;
  role: Role;
  text: string;
};
