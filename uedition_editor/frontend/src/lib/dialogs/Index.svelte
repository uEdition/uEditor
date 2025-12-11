<script lang="ts">
  import UEditorNewBranch from "./ueditor/NewBranch.svelte";
  import UEditorDeleteBranch from "./ueditor/DeleteBranch.svelte";
  import UEditorImportRemoteBranch from "./ueditor/ImportRemoteBranch.svelte";
  import UEditorMergeFromDefault from "./ueditor/MergeFromDefault.svelte";
  import FolderCreate from "./folder/Create.svelte";
  import FolderDelete from "./folder/Delete.svelte";
  import FolderRename from "./folder/Rename.svelte";
  import FileCreate from "./file/Create.svelte";
  import FileDelete from "./file/Delete.svelte";
  import FileRename from "./file/Rename.svelte";
  import FileReplace from "./file/Replace.svelte";
  import FileUpload from "./file/Upload.svelte";
  import { appState, Dialogs } from "../../state.svelte";
</script>

{#if appState.activeDialog === Dialogs.UEDITOR_NEW_BRANCH}
  <UEditorNewBranch />
{:else if appState.activeDialog === Dialogs.UEDITOR_IMPORT_REMOTE_BRANCH}
  <UEditorImportRemoteBranch />
{:else if appState.activeDialog === Dialogs.UEDITOR_DELETE_BRANCH}
  <UEditorDeleteBranch />
{:else if appState.activeDialog === Dialogs.UEDITOR_MERGE_FROM_DEFAULT}
  <UEditorMergeFromDefault />
{:else if appState.activeDialog === Dialogs.FOLDER_CREATE}
  <FolderCreate />
{:else if appState.activeDialog === Dialogs.FOLDER_DELETE}
  <FolderDelete />
{:else if appState.activeDialog === Dialogs.FOLDER_RENAME}
  <FolderRename />
{:else if appState.activeDialog === Dialogs.FILE_CREATE}
  <FileCreate />
{:else if appState.activeDialog === Dialogs.FILE_DELETE}
  <FileDelete />
{:else if appState.activeDialog === Dialogs.FILE_RENAME}
  <FileRename />
{:else if appState.activeDialog === Dialogs.FILE_REPLACE}
  <FileReplace />
{:else if appState.activeDialog === Dialogs.FILE_UPLOAD}
  <FileUpload />
{/if}
