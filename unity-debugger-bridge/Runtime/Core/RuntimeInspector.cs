using AIDebugger.Core;
#pragma warning disable CS0619
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace AIDebugger.Core
{
    public static class RuntimeInspector
    {
        private const BindingFlags AllFlags = BindingFlags.Public | BindingFlags.NonPublic |
                                             BindingFlags.Instance | BindingFlags.Static |
                                             BindingFlags.FlattenHierarchy;

        public static List<GameObjectNode> GetHierarchyTree(int maxDepth = 4, bool includeInactive = true)
        {
            var result = new List<GameObjectNode>();
            var activeScene = SceneManager.GetActiveScene();
            var rootObjects = activeScene.GetRootGameObjects();

            foreach (var root in rootObjects)
            {
                if (!includeInactive && !root.activeInHierarchy) continue;
                result.Add(SerializeGameObject(root, 0, maxDepth, includeInactive));
            }
            return result;
        }

        private static GameObjectNode SerializeGameObject(GameObject go, int currentDepth, int maxDepth, bool includeInactive)
        {
            var node = new GameObjectNode
            {
                instanceId = go.GetHashCode(),
                name = go.name,
                tag = go.tag,
                layer = go.layer,
                activeSelf = go.activeSelf,
                activeInHierarchy = go.activeInHierarchy
            };

            foreach (var comp in go.GetComponents<Component>())
            {
                if (comp == null) continue;
                node.components.Add(SerializeComponent(comp));
            }

            if (currentDepth < maxDepth)
            {
                for (int i = 0; i < go.transform.childCount; i++)
                {
                    var child = go.transform.GetChild(i).gameObject;
                    if (!includeInactive && !child.activeInHierarchy) continue;
                    node.children.Add(SerializeGameObject(child, currentDepth + 1, maxDepth, includeInactive));
                }
            }
            return node;
        }

        public static ComponentInfo SerializeComponent(Component comp)
        {
            var type = comp.GetType();
            bool isEn = comp is Behaviour b ? b.enabled : true;
            var info = new ComponentInfo
            {
                type = type.Name,
                typeName = type.Name,
                assemblyQualifiedName = type.AssemblyQualifiedName,
                isMonoBehaviour = comp is MonoBehaviour,
                isEnabled = isEn,
                enabled = isEn
            };

            foreach (var field in type.GetFields(AllFlags))
            {
                if (field.IsSpecialName) continue;
                try
                {
                    var val = field.GetValue(comp);
                    info.fields[field.Name] = FormatValue(val);
                }
                catch (Exception ex)
                {
                    info.fields[field.Name] = "<Error: " + ex.Message + ">";
                }
            }

            foreach (var prop in type.GetProperties(AllFlags))
            {
                if (!prop.CanRead || prop.GetIndexParameters().Length > 0) continue;
                if (prop.Name == "mesh" || prop.Name == "material" || prop.Name == "materials") continue;
                try
                {
                    var val = prop.GetValue(comp, null);
                    info.properties[prop.Name] = FormatValue(val);
                }
                catch { }
            }
            return info;
        }

        public static GameObjectDetails GetGameObjectDetails(int instanceId)
        {
            var go = FindGameObjectByInstanceId(instanceId);
            if (go == null) return null;
            var details = new GameObjectDetails
            {
                instanceId = go.GetHashCode(),
                name = go.name,
                tag = go.tag,
                layer = go.layer,
                activeSelf = go.activeSelf,
                isStatic = go.isStatic,
                position = new float[] { go.transform.position.x, go.transform.position.y, go.transform.position.z },
                rotation = new float[] { go.transform.rotation.x, go.transform.rotation.y, go.transform.rotation.z, go.transform.rotation.w },
                scale = new float[] { go.transform.localScale.x, go.transform.localScale.y, go.transform.localScale.z }
            };
            foreach (var comp in go.GetComponents<Component>())
            {
                if (comp != null) details.components.Add(SerializeComponent(comp));
            }
            return details;
        }

        public static GameObjectDetails InspectGameObject(int instanceId) => GetGameObjectDetails(instanceId);

        public static bool SetPropertyValue(int instanceId, string componentTypeName, string propertyOrFieldName, string serializedValue)
        {
            return SetMemberValue(instanceId, componentTypeName, propertyOrFieldName, serializedValue);
        }

        public static bool SetComponentProperty(int instanceId, string componentTypeName, string propertyOrFieldName, string serializedValue)
        {
            return SetMemberValue(instanceId, componentTypeName, propertyOrFieldName, serializedValue);
        }

        public static List<Dictionary<string, object>> FindGameObjects(string namePattern = null, string tag = null, string typeName = null)
        {
            var list = new List<Dictionary<string, object>>();
            var allObjects = UnityCompat.FindAll<GameObject>(true);

            foreach (var go in allObjects)
            {
                bool matchName = string.IsNullOrEmpty(namePattern) || go.name.IndexOf(namePattern, StringComparison.OrdinalIgnoreCase) >= 0;
                bool matchTag = string.IsNullOrEmpty(tag) || go.CompareTag(tag);
                bool matchType = true;

                if (!string.IsNullOrEmpty(typeName))
                {
                    matchType = false;
                    foreach (var c in go.GetComponents<Component>())
                    {
                        if (c != null && c.GetType().Name.IndexOf(typeName, StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            matchType = true;
                            break;
                        }
                    }
                }

                if (matchName && matchTag && matchType)
                {
                    list.Add(new Dictionary<string, object>
                    {
                        { "instanceId", go.GetHashCode() },
                        { "name", go.name },
                        { "tag", go.tag },
                        { "activeInHierarchy", go.activeInHierarchy },
                        { "position", new { x = go.transform.position.x, y = go.transform.position.y, z = go.transform.position.z } },
                        { "componentCount", go.GetComponents<Component>().Length }
                    });
                }
            }
            return list;
        }

        public static bool SetMemberValue(int instanceId, string componentTypeName, string memberName, object rawValue)
        {
            var target = FindTargetComponent(instanceId, componentTypeName);
            if (target == null) return false;

            var type = target.GetType();
            var field = type.GetField(memberName, AllFlags);
            if (field != null)
            {
                var converted = ConvertToType(rawValue, field.FieldType);
                field.SetValue(target, converted);
                return true;
            }

            var prop = type.GetProperties(AllFlags);
            foreach (var p in prop)
            {
                if (p.Name == memberName && p.CanWrite)
                {
                    var converted = ConvertToType(rawValue, p.PropertyType);
                    p.SetValue(target, converted, null);
                    return true;
                }
            }
            return false;
        }

        public static object InvokeMethod(int instanceId, string componentTypeName, string methodName, object[] args)
        {
            var target = FindTargetComponent(instanceId, componentTypeName);
            if (target == null) throw new InvalidOperationException("Target component " + componentTypeName + " not found");

            var type = target.GetType();
            var method = type.GetMethod(methodName, AllFlags);
            if (method == null) throw new MissingMethodException(type.Name, methodName);

            var parameters = method.GetParameters();
            var convertedArgs = new object[parameters.Length];
            for (int i = 0; i < parameters.Length; i++)
            {
                object raw = (args != null && i < args.Length) ? args[i] : null;
                convertedArgs[i] = ConvertToType(raw, parameters[i].ParameterType);
            }
            return method.Invoke(target, convertedArgs);
        }

        public static bool SetComponentActive(int instanceId, string componentTypeName, bool active)
        {
            var comp = FindTargetComponent(instanceId, componentTypeName);
            if (comp is Behaviour b) { b.enabled = active; return true; }
            if (comp is Collider c) { c.enabled = active; return true; }
            if (comp is Collider2D c2d) { c2d.enabled = active; return true; }
            return false;
        }

        public static bool SetGameObjectActive(int instanceId, bool active)
        {
            var go = FindGameObjectByInstanceId(instanceId);
            if (go != null) { go.SetActive(active); return true; }
            return false;
        }

        private static Component FindTargetComponent(int instanceId, string componentTypeName)
        {
            var go = FindGameObjectByInstanceId(instanceId);
            if (go == null) return null;

            foreach (var comp in go.GetComponents<Component>())
            {
                if (comp != null && comp.GetType().Name.Equals(componentTypeName, StringComparison.OrdinalIgnoreCase))
                    return comp;
            }
            return null;
        }

        private static GameObject FindGameObjectByInstanceId(int instanceId)
        {
            foreach (var go in UnityCompat.FindAll<GameObject>(true))
            {
                if (go.GetHashCode() == instanceId) return go;
            }
            return null;
        }

        private static object FormatValue(object val)
        {
            if (val == null) return null;
            if (val is Vector2 v2) return new { x = v2.x, y = v2.y };
            if (val is Vector3 v3) return new { x = v3.x, y = v3.y, z = v3.z };
            if (val is Vector4 v4) return new { x = v4.x, y = v4.y, z = v4.z, w = v4.w };
            if (val is Quaternion q) return new { x = q.x, y = q.y, z = q.z, w = q.w };
            if (val is Color col) return new { r = col.r, g = col.g, b = col.b, a = col.a };
            if (val is Component c) return new { instanceId = c.GetHashCode(), name = c.name, type = c.GetType().Name };
            if (val is GameObject g) return new { instanceId = g.GetHashCode(), name = g.name };
            if (val is ICollection colList && !(val is string))
            {
                var list = new List<object>();
                foreach (var item in colList)
                {
                    list.Add(FormatValue(item));
                    if (list.Count >= 20) { list.Add("... (truncated)"); break; }
                }
                return list;
            }
            if (val.GetType().IsPrimitive || val is string || val is decimal) return val;
            return val.ToString();
        }

        private static object ConvertToType(object val, Type targetType)
        {
            if (val == null) return targetType.IsValueType ? Activator.CreateInstance(targetType) : null;
            if (targetType.IsAssignableFrom(val.GetType())) return val;

            string str = val.ToString();
            if (targetType == typeof(int)) return int.Parse(str, CultureInfo.InvariantCulture);
            if (targetType == typeof(float)) return float.Parse(str, CultureInfo.InvariantCulture);
            if (targetType == typeof(double)) return double.Parse(str, CultureInfo.InvariantCulture);
            if (targetType == typeof(bool)) return bool.Parse(str);
            if (targetType == typeof(string)) return str;
            if (targetType.IsEnum) return Enum.Parse(targetType, str, true);

            if (targetType == typeof(Vector2) && val is string v2Str)
            {
                var parts = v2Str.Split(',');
                return new Vector2(float.Parse(parts[0], CultureInfo.InvariantCulture), float.Parse(parts[1], CultureInfo.InvariantCulture));
            }
            if (targetType == typeof(Vector3) && val is string v3Str)
            {
                var parts = v3Str.Split(',');
                return new Vector3(float.Parse(parts[0], CultureInfo.InvariantCulture), float.Parse(parts[1], CultureInfo.InvariantCulture), float.Parse(parts[2], CultureInfo.InvariantCulture));
            }
            return Convert.ChangeType(val, targetType, CultureInfo.InvariantCulture);
        }
    }
}