export type Role = "user" | "assistant" | "error";

export type Message = {
  id: string;
  role: Role;
  text: string;
};
