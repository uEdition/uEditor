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

type TipTapAttribtes = { [key: string]: string };

type TipTapMark = {
  type: string;
  attributes: TipTapAttribtes;
};
type TipTapBlock = {
  type: string;
  attributes: TipTapAttributes;
  content: TipTapNode[];
};

type TipTapText = {
  type: "text";
  marks: TipTapMark[];
  text: string;
};

type TipTapNode = TipTapText | TipTapBlock;

type TipTapDocument = {
  type: "doc";
  content: TipTapNode[];
};

type TEIMetadataSection = { name: string; title: string; type: "metadata" };

type TEITextSection = {
  name: string;
  title: string;
  type: "text";
  content: TipTapDocument;
};

type TEITextlistDocument = {
  attributes: { [key: string]: value };
  content: TipTapDocument;
};

type TEITextlistSection = {
  name: string;
  title: string;
  type: "textlist";
  content: TEITextlistDocument[];
};
type TEIDocument = {
  [key: string]: TEIMetadataSection | TEITextSection | TEITextlistSection;
};
