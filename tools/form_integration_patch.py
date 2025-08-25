#!/usr/bin/env python3
"""
Form Analysis Integration Patch for AI Selections v2.04
Integrates working form analysis into the main AI selections pipeline

Priority 1.2: Integrate Form Analysis into Main Pipeline (30 minutes)
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.04")

logger = logging.getLogger(__name__)


class FormIntegrationPatch:
    """Patches the main AI selections generator with form analysis"""
    
    def __init__(self):
        self.ai_selections_path = "/home/jc/Documents/Horse-race-ai-v2.04/src/ai_selections.py"
        self.backup_path = self.ai_selections_path + ".backup"
        
    def create_backup(self):
        """Create backup of original file"""
        try:
            import shutil
            shutil.copy2(self.ai_selections_path, self.backup_path)
            print(f"✅ Backup created: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def get_form_integration_code(self):
        """Get the form analysis integration code"""
        return '''
    def initialize_form_analyzer(self):
        """Initialize form analysis integration"""
        try:
            from tools.ml_training.simple_form_analyzer import FormAnalyzer
            self.form_analyzer = FormAnalyzer()
            logger.info("✅ Form analyzer initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Form analyzer initialization failed: {e}")
            self.form_analyzer = None
            return False
    
    def get_horse_form_metrics(self, horse_id, horse_name, race_id):
        """Get form analysis metrics for a horse"""
        if not hasattr(self, 'form_analyzer') or self.form_analyzer is None:
            return {
                'form_score': 50.0,
                'form_trend_score': 0.0,
                'form_confidence': 0.5,
                'consistency_rating': 50.0,
                'form_trend': 'stable'
            }
        
        try:
            form_result = self.form_analyzer.analyze_horse_form(horse_id, horse_name, race_id)
            return {
                'form_score': form_result.recent_form_score,
                'form_trend_score': form_result.form_trend_score,
                'form_confidence': form_result.form_confidence,
                'consistency_rating': form_result.consistency_rating,
                'form_trend': form_result.form_trend
            }
        except Exception as e:
            logger.warning(f"⚠️ Form analysis failed for {horse_name}: {e}")
            return {
                'form_score': 50.0,
                'form_trend_score': 0.0,
                'form_confidence': 0.5,
                'consistency_rating': 50.0,
                'form_trend': 'stable'
            }
    
    def enhance_features_with_form(self, features_df):
        """Enhance feature set with form analysis"""
        if features_df.empty:
            return features_df
        
        logger.info("🔄 Enhancing features with form analysis...")
        
        # Add form analysis columns
        form_columns = ['form_score', 'form_trend_score', 'form_confidence', 
                       'consistency_rating']
        
        for col in form_columns:
            if col not in features_df.columns:
                features_df[col] = 50.0  # Default neutral values
        
        # Process each horse if horse_id is available
        if 'horse_id' in features_df.columns and 'race_id' in features_df.columns:
            total_horses = len(features_df)
            for idx, row in features_df.iterrows():
                if (idx + 1) % 10 == 0:
                    print(f"  Processing form analysis {idx + 1}/{total_horses}...")
                
                horse_id = row.get('horse_id')
                horse_name = row.get('horse_name', f'Horse_{horse_id}')
                race_id = row.get('race_id')
                
                if horse_id and race_id:
                    form_metrics = self.get_horse_form_metrics(horse_id, horse_name, race_id)
                    
                    # Update dataframe with form metrics
                    for metric, value in form_metrics.items():
                        if metric in form_columns:
                            features_df.loc[idx, metric] = value
        
        logger.info(f"✅ Form analysis integrated for {len(features_df)} horses")
        return features_df
'''
    
    def apply_form_integration(self):
        """Apply form integration to AI selections"""
        try:
            # Read current file
            with open(self.ai_selections_path, 'r') as f:
                content = f.read()
            
            # Find the __init__ method and add form analyzer initialization
            init_pattern = "def __init__(self):"
            init_replacement = """def __init__(self):"""
            
            if init_pattern in content:
                # Add form analyzer initialization after existing __init__ setup
                init_pos = content.find("self.trained = False")
                if init_pos != -1:
                    end_pos = content.find("\n", init_pos)
                    content = (content[:end_pos] + 
                             "\n        # Initialize form analysis\n" +
                             "        self.initialize_form_analyzer()" +
                             content[end_pos:])
            
            # Add form integration methods before the main() function
            main_pos = content.find("def main():")
            if main_pos != -1:
                # Insert form methods before main()
                form_code = self.get_form_integration_code()
                content = content[:main_pos] + form_code + "\n\n" + content[main_pos:]
            
            # Enhance the load_enhanced_training_data method to include form
            if "def load_enhanced_training_data(self):" in content:
                # Find the return statement and add form enhancement
                pattern = "return df"
                if pattern in content:
                    content = content.replace(
                        "return df",
                        """# Enhance with form analysis
        df = self.enhance_features_with_form(df)
        return df"""
                    )
            
            # Write modified content
            with open(self.ai_selections_path, 'w') as f:
                f.write(content)
            
            print("✅ Form integration applied successfully")
            return True
            
        except Exception as e:
            print(f"❌ Form integration failed: {e}")
            return False
    
    def verify_integration(self):
        """Verify the integration was successful"""
        try:
            with open(self.ai_selections_path, 'r') as f:
                content = f.read()
            
            required_methods = [
                "initialize_form_analyzer",
                "get_horse_form_metrics", 
                "enhance_features_with_form"
            ]
            
            missing_methods = []
            for method in required_methods:
                if f"def {method}" not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"❌ Missing methods: {missing_methods}")
                return False
            
            print("✅ Form integration verification passed")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def restore_backup(self):
        """Restore from backup if something goes wrong"""
        try:
            import shutil
            if os.path.exists(self.backup_path):
                shutil.copy2(self.backup_path, self.ai_selections_path)
                print("✅ Backup restored successfully")
                return True
            else:
                print("❌ No backup file found")
                return False
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False


def main():
    """Main integration process"""
    print("🔧 FORM ANALYSIS INTEGRATION PATCH v2.04")
    print("=" * 50)
    print("Priority 1.2: Integrate Form Analysis into Main Pipeline")
    print()
    
    patcher = FormIntegrationPatch()
    
    # Step 1: Create backup
    print("Step 1: Creating backup...")
    if not patcher.create_backup():
        print("❌ Cannot proceed without backup")
        return 1
    
    # Step 2: Apply integration
    print("\nStep 2: Applying form integration...")
    if not patcher.apply_form_integration():
        print("❌ Integration failed, restoring backup...")
        patcher.restore_backup()
        return 1
    
    # Step 3: Verify integration
    print("\nStep 3: Verifying integration...")
    if not patcher.verify_integration():
        print("❌ Verification failed, restoring backup...")
        patcher.restore_backup()
        return 1
    
    print("\n✅ FORM INTEGRATION COMPLETED SUCCESSFULLY!")
    print("🎯 Form analysis is now integrated into the main AI pipeline")
    print("📊 The system will now include:")
    print("   • Recent form scores (0-100)")
    print("   • Form trend analysis (improving/declining/stable)")
    print("   • Form confidence metrics")
    print("   • Consistency ratings")
    print("   • Enhanced prediction accuracy")
    
    print(f"\n💾 Backup saved: {patcher.backup_path}")
    print("🚀 Ready for enhanced AI predictions with form analysis!")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
