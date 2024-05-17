/// <reference types="svelte" />
/// <reference types="vite/client" />

type Config = {};

type UEditionAuthor = {
  name: string | null;
  email: string | null;
};

type UEditionLanguage = {
  code: string;
  label: string;
  path: string;
};

type UEditionOutput = {
  path: string;
  tei: boolean;
};

type UEditionRepository = {
  url: string | null;
  branch: string | null;
};

type UEditionTitle = {
  [x: string]: string;
};

type UEditionSettings = {
  version: "1";
  author: UEditionAuthor;
  languages: UEditionLanguage[];
  output: UEditionOutput;
  repository: UEditionRepository;
  title: UEditionTitle;
  jb_config: any;
};

type UEditorSettings = any;

type FileTreeEntry = {
  name: string;
  fullpath: string;
  type: "file" | "folder";
  content?: FileTreeEntry[];
  mimetype: string;
};

type LoadTextFileAction = {
  action: "LoadTextFile";
  branch: string;
  filename: string;
  callback: (data: string) => void;
  status?: string;
};

type SaveCurrentFileAction = {
  action: "SaveCurrentFile";
  branch: string;
  filename: string;
  data: string;
  callback: () => void;
  status?: string;
};

type Action = LoadTextFileAction | SaveCurrentFileAction;
