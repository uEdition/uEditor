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

type UEditorValueTitlePair = {
  value: string;
  title: string;
};

type UEditorTEIAttribute = {
  name: string;
  value: string | null;
  type: "string" | "static" | "id-ref";
  default: string;
};

type UEditorTEINode = {
  name: string;
  selector: string;
  attributes: UEditorTEIAttribute[];
  tag: string | null;
};

type UEditorTEIMetadataSection = {
  name: string;
  title: string;
  type: "metadata";
  selector: string;
};

type UEditorTEIMenuItemSetBlock = {
  type: "set-block";
  block: string;
  title: string;
  icon: string | null;
};

type UEditorTEIMenuItemToggleMark = {
  type: "toggle-mark";
  mark: string;
  title: string;
  icon: string | null;
};

type UEditorTEIMenuCondition = {
  node: string;
};

type TEITextToolbarBlock = {
  title: string;
  type: "toolbar";
  items: (UEditorTEIMenuItemSetBlock | UEditorTEIMenuItemToggleMark)[];
  condition: UEditorTEIMenuCondition | null;
};

type UEditorTEISelectBlockAttribute = {
  type: "select-block-attribute";
  block: string;
  name: string;
  title: string;
  values: UEditorValueTitlePair[];
};

type UEditorTEISelectCrossReferenceMarkAttribute = {
  type: "select-cross-reference-attribute";
  mark: string;
  name: string;
  title: string;
  section: string;
};

type UEditorTEITextFormBlock = {
  title: string;
  type: "form";
  items: (
    | UEditorTEISelectBlockAttribute
    | UEditorTEISelectCrossReferenceMarkAttribute
  )[];
  condition: UEditorTEIMenuCondition | null;
};

type UEditorTEITextSection = {
  name: string;
  title: string;
  type: "text";
  selector: string;
  sidebar: (UEditorTEITextFormBlock | TEITextToolbarBlock)[];
};

type UEditorTEITextListSection = {
  name: string;
  title: string;
  type: "textlist";
  selector: string;
  sidebar: (UEditorTEITextFormBlock | TEITextToolbarBlock)[];
};

type UEditorTEISettings = {
  blocks: UEditorTEINode[];
  marks: UEditorTEINode[];
  sections: (
    | UEditorTEIMetadataSection
    | UEditorTEITextSection
    | UEditorTEITextListSection
  )[];
};

type UEditorTEIActions =
  | UEditorTEIMenuItemSetBlock
  | UEditorTEIMenuItemToggleMark
  | UEditorTEISelectBlockAttribute
  | UEditorTEISelectCrossReferenceMarkAttribute;

type UEditorSettings = { tei: UEditorTEISettings };

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
  attrs: TipTapAttribtes;
};

type TipTapBlock = {
  type: string;
  attrs: TipTapAttributes;
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

type TEIMetadataSection = {
  name: string;
  title: string;
  type: UEditorTEIMetadataSection;
};

type TEITextSection = {
  name: string;
  title: string;
  type: UEditorTEITextSection;
  content: TipTapDocument;
};

type TEITextlistDocument = {
  attrs: { id: string };
  content: TipTapDocument;
};

type TEITextlistSection = {
  name: string;
  title: string;
  type: UEditorTEITextListSection;
  content: TEITextlistDocument[];
};

type TEIDocument = (TEIMetadataSection | TEITextSection | TEITextlistSection)[];
