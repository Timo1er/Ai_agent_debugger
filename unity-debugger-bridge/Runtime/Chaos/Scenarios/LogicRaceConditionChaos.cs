using System;
using UnityEngine;
using AIDebugger.Chaos;

namespace AIDebugger.Chaos.Scenarios
{
    public class LogicRaceConditionChaos : ChaosScenarioBase
    {
        public override string ScenarioName => "logic_race_condition";
        public override string Description => "Desynchronizes game state machines, forcing conflicting states (e.g., IsStunned=true while IsAttacking=true and CanMove=false) causing character state lockup.";

        public bool isPlayerLocked = false;
        public string currentState = "NORMAL";

        public override bool Inject(string parametersJson)
        {
            IsActive = true;
            isPlayerLocked = true;
            currentState = "STALEMATE_DESYNC";
            Debug.LogWarning("[StateMachine] Detected invalid race condition state: IsStunned=true, IsAttacking=true, CanMove=false. Character state machine locked.");
            return true;
        }

        public override void Revert()
        {
            IsActive = false;
            isPlayerLocked = false;
            currentState = "NORMAL";
        }

        public override object GetStatus()
        {
            return new
            {
                isPlayerLocked = isPlayerLocked,
                currentState = currentState
            };
        }
    }
}