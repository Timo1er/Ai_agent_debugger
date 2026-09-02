#pragma warning disable CS0619
using System;
using System.Diagnostics;
using System.Text;
using UnityEngine;

namespace AIDebugger.Core
{
    public static class DynamicCodeEvaluator
    {
        public static DynamicCodeResult Execute(string codeSnippet)
        {
            var sw = Stopwatch.StartNew();
            var logBuffer = new StringBuilder();

            void LogHandler(string logString, string stackTrace, LogType type)
            {
                logBuffer.AppendLine("[" + type + "] " + logString);
            }

            Application.logMessageReceived += LogHandler;

            try
            {
                object result = ExecuteInternal(codeSnippet);
                sw.Stop();

                return new DynamicCodeResult
                {
                    success = true,
                    returnValue = result != null ? result.ToString() : "void / null",
                    logs = logBuffer.ToString(),
                    executionTimeMs = sw.Elapsed.TotalMilliseconds
                };
            }
            catch (Exception ex)
            {
                sw.Stop();
                return new DynamicCodeResult
                {
                    success = false,
                    error = ex.InnerException != null ? ex.InnerException.ToString() : ex.ToString(),
                    logs = logBuffer.ToString(),
                    executionTimeMs = sw.Elapsed.TotalMilliseconds
                };
            }
            finally
            {
                Application.logMessageReceived -= LogHandler;
            }
        }

        private static object ExecuteInternal(string codeSnippet)
        {
            if (string.IsNullOrWhiteSpace(codeSnippet)) return "Empty code snippet";

            var lines = codeSnippet.Split(new[] { ';', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries);
            object lastResult = null;

            foreach (var rawLine in lines)
            {
                var line = rawLine.Trim();
                if (string.IsNullOrEmpty(line) || line.StartsWith("//")) continue;

                if (line.StartsWith("SET ", StringComparison.OrdinalIgnoreCase))
                {
                    lastResult = ExecuteSetCommand(line.Substring(4).Trim());
                }
                else if (line.StartsWith("INVOKE ", StringComparison.OrdinalIgnoreCase))
                {
                    lastResult = ExecuteInvokeCommand(line.Substring(7).Trim());
                }
                else if (line.Contains("=") && !line.Contains("=="))
                {
                    lastResult = ExecuteSetCommand(line);
                }
                else if (line.Contains("(") && line.Contains(")"))
                {
                    lastResult = ExecuteInvokeCommand(line);
                }
            }

            return lastResult ?? "Dynamic execution completed.";
        }

        private static object ExecuteSetCommand(string expression)
        {
            var parts = expression.Split(new[] { '=' }, 2);
            if (parts.Length != 2) throw new ArgumentException("SET format: ObjectName.ComponentName.Member = Value");

            string left = parts[0].Trim();
            string right = parts[1].Trim();

            var leftParts = left.Split('.');
            if (leftParts.Length < 3) throw new ArgumentException("Target format must be ObjectName.ComponentName.Member");

            string objName = leftParts[0];
            string compName = leftParts[1];
            string member = leftParts[2];

            var go = GameObject.Find(objName);
            if (go == null) throw new NullReferenceException("GameObject '" + objName + "' not found.");

            bool ok = RuntimeInspector.SetMemberValue(go.GetHashCode(), compName, member, ParseLiteral(right));
            return ok ? "Successfully set " + left + " = " + right : "Failed to set member " + member;
        }

        private static object ExecuteInvokeCommand(string expression)
        {
            int parenOpen = expression.IndexOf('(');
            int parenClose = expression.LastIndexOf(')');
            if (parenOpen < 0 || parenClose < parenOpen) throw new ArgumentException("INVOKE format: ObjectName.ComponentName.Method(args)");

            string left = expression.Substring(0, parenOpen).Trim();
            string argsStr = expression.Substring(parenOpen + 1, parenClose - parenOpen - 1).Trim();

            var leftParts = left.Split('.');
            if (leftParts.Length < 3) throw new ArgumentException("Target format must be ObjectName.ComponentName.Method");

            string objName = leftParts[0];
            string compName = leftParts[1];
            string methodName = leftParts[2];

            var go = GameObject.Find(objName);
            if (go == null) throw new NullReferenceException("GameObject '" + objName + "' not found.");

            var rawArgs = string.IsNullOrEmpty(argsStr) ? new object[0] : ParseArgs(argsStr);
            var res = RuntimeInspector.InvokeMethod(go.GetHashCode(), compName, methodName, rawArgs);
            return res ?? "Execution successful (null/void)";
        }

        private static object[] ParseArgs(string argsStr)
        {
            var tokens = argsStr.Split(',');
            var list = new object[tokens.Length];
            for (int i = 0; i < tokens.Length; i++)
            {
                list[i] = ParseLiteral(tokens[i].Trim());
            }
            return list;
        }

        private static object ParseLiteral(string raw)
        {
            if (bool.TryParse(raw, out bool b)) return b;
            if (int.TryParse(raw, out int i)) return i;
            if (float.TryParse(raw, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float f)) return f;
            if (raw.StartsWith("\"") && raw.EndsWith("\"")) return raw.Substring(1, raw.Length - 2);
            return raw;
        }
    }
}