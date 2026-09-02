using System;
using UnityEngine;

namespace AIDebugger.Core
{
    public class TimeStepController : MonoBehaviour
    {
        private static TimeStepController _instance;
        public static TimeStepController Instance => _instance;

        private float _previousTimeScale = 1.0f;
        private bool _isPaused = false;
        private int _framesToStep = 0;
        private Action _onStepComplete;

        public bool IsPaused => _isPaused;
        public float CurrentTimeScale => Time.timeScale;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private void LateUpdate()
        {
            if (_framesToStep > 0)
            {
                _framesToStep--;
                if (_framesToStep <= 0)
                {
                    Time.timeScale = 0f;
                    _isPaused = true;
                    _onStepComplete?.Invoke();
                    _onStepComplete = null;
                }
            }
        }

        public void SetTimeScale(float scale)
        {
            scale = Mathf.Clamp(scale, 0f, 100f);
            Time.timeScale = scale;
            if (scale > 0f)
            {
                _previousTimeScale = scale;
                _isPaused = false;
            }
            else
            {
                _isPaused = true;
            }
        }

        public void Pause()
        {
            if (!_isPaused)
            {
                _previousTimeScale = Time.timeScale > 0 ? Time.timeScale : 1.0f;
                Time.timeScale = 0f;
                _isPaused = true;
            }
        }

        public void Resume()
        {
            if (_isPaused)
            {
                Time.timeScale = _previousTimeScale > 0 ? _previousTimeScale : 1.0f;
                _isPaused = false;
            }
        }

        public void StepFrames(int frameCount, Action onComplete = null)
        {
            if (frameCount <= 0) frameCount = 1;
            _framesToStep = frameCount;
            _onStepComplete = onComplete;
            Time.timeScale = 1.0f;
            _isPaused = false;
        }
    }
}
