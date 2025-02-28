<script context="module" lang="ts">
  import { writable } from "svelte/store";

  export enum Dialogs {
    NONE = 1,

    UEDITOR_NEW_BRANCH,
    UEDITOR_IMPORT_REMOTE_BRANCH,
    UEDITOR_DELETE_BRANCH,

    FOLDER_CREATE,
    FOLDER_DELETE,
    FOLDER_RENAME,

    FILE_CREATE,
    FILE_DELETE,
    FILE_RENAME,
    FILE_UPLOAD,
  }

  export const activeDialog = writable(Dialogs.NONE);
</script>

<script lang="ts">
  import UEditorNewBranch from "./ueditor/NewBranch.svelte";
  import UEditorDeleteBranch from "./ueditor/DeleteBranch.svelte";
  import UEditorImportRemoteBranch from "./ueditor/ImportRemoteBranch.svelte";
  import FolderCreate from "./folder/Create.svelte";
  import FolderDelete from "./folder/Delete.svelte";
  import FolderRename from "./folder/Rename.svelte";
  import FileCreate from "./file/Create.svelte";
  import FileDelete from "./file/Delete.svelte";
  import FileRename from "./file/Rename.svelte";
  import FileUpload from "./file/Upload.svelte";
</script>

{#if $activeDialog === Dialogs.UEDITOR_NEW_BRANCH}
  <UEditorNewBranch />
{:else if $activeDialog === Dialogs.UEDITOR_IMPORT_REMOTE_BRANCH}
  <UEditorImportRemoteBranch />
{:else if $activeDialog === Dialogs.UEDITOR_DELETE_BRANCH}
  <UEditorDeleteBranch />
{:else if $activeDialog === Dialogs.FOLDER_CREATE}
  <FolderCreate />
{:else if $activeDialog === Dialogs.FOLDER_DELETE}
  <FolderDelete />
{:else if $activeDialog === Dialogs.FOLDER_RENAME}
  <FolderRename />
{:else if $activeDialog === Dialogs.FILE_CREATE}
  <FileCreate />
{:else if $activeDialog === Dialogs.FILE_DELETE}
  <FileDelete />
{:else if $activeDialog === Dialogs.FILE_RENAME}
  <FileRename />
{:else if $activeDialog === Dialogs.FILE_UPLOAD}
  <FileUpload />
{/if}
